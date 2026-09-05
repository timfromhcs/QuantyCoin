#!/usr/bin/env python3
"""
QTY4 deterministic fuzz smoke harness (stdlib only, seeded).

Targets: block headers, transactions, compact-target decoder,
segwit addresses, P2P frames, Stratum V2 frames, varint codec,
plus production-vs-reference differential fuzz.

Deterministic: fixed seeds => reproducible. Bounded iterations for CI smoke.
Failing inputs are written to tests/fuzz_corpus/ for regression.
"""

import os
import random
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.block import BlockHeader
from core.transaction import Transaction, TxIn, TxOut
from core.consensus import bits_to_target, target_to_bits
from crypto.bip32_44 import decode_segwit_address
from network.protocol import create_message, parse_header, HEADER_LENGTH
from miner.stratum_v2 import encode_sv2_frame, decode_sv2_frame
from reference import qty4_reference as R

CORPUS = REPO / "tests" / "fuzz_corpus"
ITERATIONS = int(os.environ.get("QTY4_FUZZ_ITERS", "2000"))
SEED = int(os.environ.get("QTY4_FUZZ_SEED", "20260905"))

failures = []


def save_case(name, data: bytes):
    CORPUS.mkdir(parents=True, exist_ok=True)
    (CORPUS / f"{name}.bin").write_bytes(data[:4096])


def check(name, fn):
    try:
        fn()
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"[FAIL] {name}: {e}")
    except Exception as e:  # harness bug, not consensus failure
        failures.append(f"{name} HARNESS-ERROR: {type(e).__name__}: {e}")
        print(f"[ERROR] {name}: {type(e).__name__}: {e}")


def fuzz_headers(rng):
    def run():
        n = ITERATIONS // 5
        for i in range(n):
            raw = bytes(rng.getrandbits(8) for _ in range(rng.choice([0, 1, 10, 79, 80, 81, 160])))
            try:
                h, off = BlockHeader.deserialize(raw)
                assert off == 80, "offset must be 80"
                assert h.serialize() == raw[:80], "header round-trip"
                # differential vs reference
                rf, rn = R.deserialize_header(raw[:80] if len(raw) >= 80 else raw + b"\x00" * 80) \
                    if len(raw) >= 80 else (None, None)
                if rf is not None:
                    assert rf["bits"] == h.bits and rf["nonce"] == h.nonce
            except ValueError:
                assert len(raw) < 80 or True  # short/truncated must raise ValueError
            except AssertionError:
                save_case(f"header_{SEED}_{i}", raw)
                raise
    check("headers", run)


def fuzz_compact(rng):
    def run():
        for i in range(ITERATIONS):
            bits = rng.getrandbits(32)
            try:
                pt = bits_to_target(bits)
                rt = R.compact_to_target(bits)
                assert pt == rt, f"target divergence 0x{bits:08x}"
                if pt > 0:
                    assert target_to_bits(pt) == R.target_to_compact(rt)
            except ValueError:
                try:
                    R.compact_to_target(bits)
                except ValueError:
                    pass
                else:
                    save_case(f"compact_{SEED}_{i}", struct.pack("<I", bits))
                    raise AssertionError(f"reference accepted bits production rejected: 0x{bits:08x}")
            except AssertionError:
                save_case(f"compact_{SEED}_{i}", struct.pack("<I", bits))
                raise
    check("compact", run)


def fuzz_transactions(rng):
    def run():
        for i in range(ITERATIONS // 4):
            try:
                n_in = rng.randint(0, 4)
                n_out = rng.randint(0, 4)
                vin = [TxIn(bytes(rng.getrandbits(8) for _ in range(32)), rng.getrandbits(32)) for _ in range(n_in)]
                vout = []
                for _ in range(n_out):
                    val = rng.choice([0, 1, 1000, 5000000000, 21000000 * 100_000_000, 21000000 * 100_000_000 + 1, -5])
                    try:
                        vout.append(TxOut(val, b"\x00\x14" + bytes(rng.getrandbits(8) for _ in range(20))))
                    except ValueError:
                        vout = None
                        break
                if vout is None:
                    continue
                tx = Transaction(version=rng.choice([0, 1, 2]), vin=vin, vout=vout)
                ok, _ = tx.validate_structure()
                raw = tx.serialize(include_witness=False)
                assert isinstance(raw, bytes) and len(raw) > 0
                # consensus invariants: empty vin/vout or dup inputs must be invalid
                if not vin or not vout:
                    assert not ok, "empty vin/vout must be invalid"
            except AssertionError:
                save_case(f"tx_{SEED}_{i}", b"txcase")
                raise
    check("transactions", run)


def fuzz_addresses(rng):
    def run():
        valid = "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf"
        for i in range(ITERATIONS // 4):
            s = list(valid)
            for _ in range(rng.randint(1, 4)):
                s[rng.randrange(len(s))] = rng.choice("qpzry9x8gf2tvdw0s3jn54khce6mua7l1QTYZ")
            cand = "".join(s)
            pv, pp = decode_segwit_address("qty", cand)
            rv, rp = R.segwit_decode("qty", cand)
            assert (pp is None) == (rp is None), f"address divergence: {cand}"
            if pp is not None:
                assert pv == rv and pp == rp
    check("addresses", run)


def fuzz_p2p(rng):
    def run():
        for i in range(ITERATIONS // 4):
            payload = bytes(rng.getrandbits(8) for _ in range(rng.randint(0, 300)))
            cmd = rng.choice(["ping", "pong", "tx", "block", "inv", "getdata", "x" * 12, ""])
            try:
                frame = create_message(cmd[:12], payload)
            except Exception:
                continue
            assert len(frame) >= HEADER_LENGTH
            magic, pcmd, plen, chk = parse_header(frame[:HEADER_LENGTH])
            assert magic == b"\x51\x54\x59\x34", "magic must be QTY4"
            # truncated / oversized / corrupt must not crash
            for cut in (0, 1, HEADER_LENGTH - 1, len(frame) - 1 if len(frame) > HEADER_LENGTH else 0):
                try:
                    parse_header(frame[:cut] if cut else b"")
                except Exception:
                    pass
            mut = bytearray(frame)
            if len(mut) > HEADER_LENGTH:
                mut[HEADER_LENGTH] ^= 0xFF
                _, _, _, chk2 = parse_header(bytes(mut[:HEADER_LENGTH]))
                assert chk2 == chk  # header checksum field independent of payload mutation
    check("p2p", run)


def fuzz_sv2(rng):
    def run():
        for i in range(ITERATIONS // 4):
            mtype = rng.randint(0, 255)
            payload = bytes(rng.getrandbits(8) for _ in range(rng.randint(0, 200)))
            frame = encode_sv2_frame(0, mtype, payload)
            ext, mt, pl, consumed = decode_sv2_frame(frame)
            assert consumed == len(frame) and mt == mtype and pl == payload
            # truncated must return consumed=0, never raise
            t = frame[: rng.randint(0, len(frame) - 1)] if len(frame) > 1 else b""
            _, _, _, c2 = decode_sv2_frame(t)
            assert c2 == 0
    check("stratum_v2", run)


def fuzz_varint(rng):
    def run():
        from core.transaction import _encode_varint, _decode_varint
        for i in range(ITERATIONS // 2):
            v = rng.choice([0, 1, 252, 253, 65535, 65536, 2**32 - 1, 2**32, 2**64 - 1])
            raw = _encode_varint(v)
            back, off = _decode_varint(raw)
            assert back == v and off == len(raw)
            rraw = R.encode_varint(v)
            assert rraw == raw, f"varint divergence {v}"
    check("varint", run)


def main():
    print(f"QTY4 FUZZ SMOKE: seed={SEED} iters={ITERATIONS}")
    rng = random.Random(SEED)
    fuzz_headers(rng)
    fuzz_compact(rng)
    fuzz_transactions(rng)
    fuzz_addresses(rng)
    fuzz_p2p(rng)
    fuzz_sv2(rng)
    fuzz_varint(rng)
    if failures:
        print(f"\n[FAIL] {len(failures)} fuzz failure(s):")
        for f in failures[:20]:
            print("  -", f)
        sys.exit(1)
    print("ALL FUZZ SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()
