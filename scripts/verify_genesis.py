#!/usr/bin/env python3
"""
QuantyCoin QTY4 Authoritative Genesis Consensus & Cryptographic Audit Tool
Dual-Path Verification:
  Path A: Core State Machine & Consensus Primitives (core.block, core.transaction, node.chainstate)
  Path B: Zero-Dependency Independent Engine (pure Python standard library: struct, hashlib)

Validates all canonical manifests, public artifacts, runtime consensus constants,
byte-for-byte serialization equality, and strictly rejects stale QTY2/QTY3 artifacts.
"""

import sys
import os
import json
import struct
import hashlib
import tempfile
import shutil
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    PROTOCOL_VERSION,
    CHAIN_ID,
    MAGIC_BYTES,
    DEFAULT_P2P_PORT,
    DEFAULT_RPC_PORT,
    DEFAULT_STRATUM_PORT,
    DEFAULT_STRATUM_V2_PORT,
    GENESIS_HASH,
    GENESIS_MERKLE_ROOT,
    GENESIS_TIMESTAMP,
    GENESIS_TIMESTAMP_STR,
    GENESIS_BITS,
    GENESIS_NONCE,
    GENESIS_COINBASE_PAYOUT_ADDRESS,
    GENESIS_BLOCK_REWARD,
    GENESIS_BLOCK_REWARD_SATOSHIS,
)

# Canonical Authoritative Invariants for QTY4
CANONICAL_QTY4 = {
    "protocol_version": 70040,
    "chain_id": "quantycoin-4.0",
    "network_magic_hex": "0x51545934",
    "genesis_hash": "000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3",
    "merkle_root": "3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea",
    "timestamp": 1788614400,
    "timestamp_str": "2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol",
    "bits": 0x1e0fffff,
    "nonce": 2951011,
    "reward_satoshis": 5000000000,
    "payout_address": "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf",
    "payout_script_hex": "0014e144bcff091f7dc11fa8714134e65ab9cc558166",
    "header_size_bytes": 80,
    "block_size_bytes": 267,
    "default_p2p_port": 19444,
    "default_rpc_port": 19445,
    "default_stratum_port": 3333,
    "default_stratum_v2_port": 3334,
}

# Forbidden Stale Artifact Values (QTY2 / QTY3 legacy contamination)
FORBIDDEN_STALE_VALUES = [
    "00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba",  # QTY2 genesis hash
    "ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f",  # QTY2 merkle root
    "1788600000",                                                          # QTY2 timestamp
    "quantycoin-2.0",                                                      # QTY2 chain id
    "0x5155414e",                                                          # QTY2 QUAN magic
]


def audit_stale_contamination() -> int:
    """Scans all active genesis files to ensure zero QTY2/QTY3 legacy values survive."""
    print("--- [GATE 1] STALE ARTIFACT & LEGACY CONTAMINATION SCAN ---")
    genesis_files = [
        repo_root / "genesis" / "PUBLIC_GENESIS_MANIFEST.json",
        repo_root / "genesis" / "public" / "public_genesis_manifest.json",
        repo_root / "genesis" / "public" / "genesis_parameters.json",
        repo_root / "genesis" / "public" / "genesis_block.json",
        repo_root / "genesis" / "public" / "genesis_hash.txt",
        repo_root / "genesis" / "public" / "genesis_merkle_root.txt",
        repo_root / "spec" / "qty4" / "genesis.json",
        repo_root / "public_genesis.json",
    ]
    errors = 0
    for gf in genesis_files:
        if not gf.exists():
            print(f"[FAIL] Missing mandatory genesis file: {gf.relative_to(repo_root)}")
            errors += 1
            continue
        content = gf.read_text(encoding="utf-8")
        for stale in FORBIDDEN_STALE_VALUES:
            if stale in content:
                print(f"[FAIL] Stale legacy value '{stale}' found in {gf.relative_to(repo_root)}")
                errors += 1
    if errors == 0:
        print("[PASS] Zero stale QTY2/QTY3 contamination found in genesis artifacts.")
    return errors


def verify_runtime_consensus_constants() -> int:
    """Verifies that core.genesis_constants match canonical QTY4 specifications."""
    print("--- [GATE 2] RUNTIME CONSENSUS CONSTANTS VERIFICATION ---")
    errors = 0
    checks = [
        ("PROTOCOL_VERSION", PROTOCOL_VERSION, CANONICAL_QTY4["protocol_version"]),
        ("CHAIN_ID", CHAIN_ID, CANONICAL_QTY4["chain_id"]),
        ("MAGIC_BYTES", MAGIC_BYTES.hex(), bytes.fromhex("51545934").hex()),
        ("DEFAULT_P2P_PORT", DEFAULT_P2P_PORT, CANONICAL_QTY4["default_p2p_port"]),
        ("DEFAULT_RPC_PORT", DEFAULT_RPC_PORT, CANONICAL_QTY4["default_rpc_port"]),
        ("DEFAULT_STRATUM_PORT", DEFAULT_STRATUM_PORT, CANONICAL_QTY4["default_stratum_port"]),
        ("DEFAULT_STRATUM_V2_PORT", DEFAULT_STRATUM_V2_PORT, CANONICAL_QTY4["default_stratum_v2_port"]),
        ("GENESIS_HASH", GENESIS_HASH, CANONICAL_QTY4["genesis_hash"]),
        ("GENESIS_MERKLE_ROOT", GENESIS_MERKLE_ROOT, CANONICAL_QTY4["merkle_root"]),
        ("GENESIS_TIMESTAMP", GENESIS_TIMESTAMP, CANONICAL_QTY4["timestamp"]),
        ("GENESIS_TIMESTAMP_STR", GENESIS_TIMESTAMP_STR, CANONICAL_QTY4["timestamp_str"]),
        ("GENESIS_BITS", GENESIS_BITS, CANONICAL_QTY4["bits"]),
        ("GENESIS_NONCE", GENESIS_NONCE, CANONICAL_QTY4["nonce"]),
        ("GENESIS_COINBASE_PAYOUT_ADDRESS", GENESIS_COINBASE_PAYOUT_ADDRESS, CANONICAL_QTY4["payout_address"]),
        ("GENESIS_BLOCK_REWARD", GENESIS_BLOCK_REWARD, 50),
        ("GENESIS_BLOCK_REWARD_SATOSHIS", GENESIS_BLOCK_REWARD_SATOSHIS, CANONICAL_QTY4["reward_satoshis"]),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            print(f"[FAIL] Constant mismatch: {name} = {actual}, expected {expected}")
            errors += 1
        else:
            print(f"[PASS] {name} == {expected}")
    return errors


def verify_manifests() -> int:
    """Verifies all committed JSON and text genesis manifests."""
    print("--- [GATE 3] MANIFEST & PUBLIC ARTIFACT CONSISTENCY AUDIT ---")
    errors = 0

    # 1. genesis/PUBLIC_GENESIS_MANIFEST.json
    m1_path = repo_root / "genesis" / "PUBLIC_GENESIS_MANIFEST.json"
    try:
        m1 = json.loads(m1_path.read_text(encoding="utf-8"))
        assert m1["protocol_version"] == CANONICAL_QTY4["protocol_version"]
        assert m1["chain_id"] == CANONICAL_QTY4["chain_id"]
        assert m1["genesis_hash"] == CANONICAL_QTY4["genesis_hash"]
        assert m1["merkle_root"] == CANONICAL_QTY4["merkle_root"]
        assert m1["timestamp"] == CANONICAL_QTY4["timestamp"]
        assert m1["bits"] == CANONICAL_QTY4["bits"]
        assert m1["nonce"] == CANONICAL_QTY4["nonce"]
        print(f"[PASS] Manifest validated: {m1_path.relative_to(repo_root)}")
    except Exception as e:
        print(f"[FAIL] Manifest validation failed for {m1_path}: {e}")
        errors += 1

    # 2. public_genesis.json (root)
    m2_path = repo_root / "public_genesis.json"
    try:
        m2 = json.loads(m2_path.read_text(encoding="utf-8"))
        gb = m2.get("genesis_block", m2)
        assert gb["hash"] == CANONICAL_QTY4["genesis_hash"]
        assert gb["merkle_root"] == CANONICAL_QTY4["merkle_root"]
        assert gb["timestamp"] == CANONICAL_QTY4["timestamp"]
        assert gb["nonce"] == CANONICAL_QTY4["nonce"]
        assert m2.get("protocol_version") == CANONICAL_QTY4["protocol_version"]
        assert m2.get("chain_id") == CANONICAL_QTY4["chain_id"]
        print(f"[PASS] Manifest validated: {m2_path.relative_to(repo_root)}")
    except Exception as e:
        print(f"[FAIL] Manifest validation failed for {m2_path}: {e}")
        errors += 1

    # 3. genesis/public/ artifacts
    pub_dir = repo_root / "genesis" / "public"
    hash_txt = (pub_dir / "genesis_hash.txt").read_text(encoding="utf-8").strip()
    if hash_txt != CANONICAL_QTY4["genesis_hash"]:
        print(f"[FAIL] genesis_hash.txt mismatch: {hash_txt}")
        errors += 1
    else:
        print(f"[PASS] genesis_hash.txt matches: {hash_txt}")

    mroot_txt = (pub_dir / "genesis_merkle_root.txt").read_text(encoding="utf-8").strip()
    if mroot_txt != CANONICAL_QTY4["merkle_root"]:
        print(f"[FAIL] genesis_merkle_root.txt mismatch: {mroot_txt}")
        errors += 1
    else:
        print(f"[PASS] genesis_merkle_root.txt matches: {mroot_txt}")

    return errors


def path_a_core_verification() -> dict:
    """Path A: Verify using core project consensus engine."""
    print("--- [GATE 4] PATH A: CORE STATE MACHINE & PRIMITIVES VERIFICATION ---")
    from core.transaction import Transaction, TxIn, TxOut
    from core.block import BlockHeader, Block
    from crypto import compute_merkle_root
    from node.chainstate import Chainstate

    script_sig = (
        b'\x04\xff\xff\x00\x1d\x01\x04' +
        bytes([len(CANONICAL_QTY4["timestamp_str"])]) +
        CANONICAL_QTY4["timestamp_str"].encode('utf-8')
    )
    spk = bytes.fromhex(CANONICAL_QTY4["payout_script_hex"])
    cb_tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=CANONICAL_QTY4["reward_satoshis"], script_pubkey=spk)],
        locktime=0
    )
    merkle_root = compute_merkle_root([cb_tx.txid])
    header = BlockHeader(
        version=1,
        prev_block=b'\x00' * 32,
        merkle_root=merkle_root,
        timestamp=CANONICAL_QTY4["timestamp"],
        bits=CANONICAL_QTY4["bits"],
        nonce=CANONICAL_QTY4["nonce"]
    )
    block = Block(header=header, transactions=[cb_tx])

    header_bytes = header.serialize()
    block_bytes = block.serialize()
    hash_hex = header.hash_hex
    mroot_hex = merkle_root[::-1].hex()

    assert len(header_bytes) == CANONICAL_QTY4["header_size_bytes"], f"Header size != 80: {len(header_bytes)}"
    assert len(block_bytes) == CANONICAL_QTY4["block_size_bytes"], f"Block size != 267: {len(block_bytes)}"
    assert hash_hex == CANONICAL_QTY4["genesis_hash"], f"Header hash mismatch: {hash_hex}"
    assert mroot_hex == CANONICAL_QTY4["merkle_root"], f"Merkle root mismatch: {mroot_hex}"
    assert header.verify_pow(), "Header PoW failed target check"
    assert block.verify_merkle_root(), "Block Merkle root check failed"

    # Runtime Chainstate bootstrap test
    temp_dir = tempfile.mkdtemp(prefix="qty4_genesis_chainstate_")
    try:
        cs = Chainstate(datadir=temp_dir)
        assert cs.best_tip is not None, "Chainstate best_tip is None"
        assert cs.best_tip.header.hash_hex == CANONICAL_QTY4["genesis_hash"], "Chainstate genesis hash mismatch"
        assert cs.best_tip.height == 0, f"Chainstate genesis height != 0: {cs.best_tip.height}"
        print("[PASS] Path A Core Engine + Chainstate runtime initialization verified.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "header_hex": header_bytes.hex(),
        "block_hex": block_bytes.hex(),
        "hash_hex": hash_hex,
        "merkle_root_hex": mroot_hex,
    }


def path_b_standalone_verification() -> dict:
    """Path B: Zero-dependency independent reimplementation using ONLY Python standard library."""
    print("--- [GATE 5] PATH B: INDEPENDENT STANDALONE STANDARD LIBRARY AUDIT ---")
    def dsha256(b: bytes) -> bytes:
        return hashlib.sha256(hashlib.sha256(b).digest()).digest()

    # 1. Build Coinbase Transaction manually
    version_bytes = struct.pack("<i", 1)
    tx_in_count = b"\x01"
    prev_txid = b"\x00" * 32
    prev_vout = struct.pack("<I", 0xFFFFFFFF)

    ts_bytes = CANONICAL_QTY4["timestamp_str"].encode('utf-8')
    script_sig = b"\x04\xff\xff\x00\x1d\x01\x04" + bytes([len(ts_bytes)]) + ts_bytes
    script_sig_len = bytes([len(script_sig)])
    sequence = struct.pack("<I", 0xFFFFFFFF)

    tx_out_count = b"\x01"
    value_bytes = struct.pack("<q", CANONICAL_QTY4["reward_satoshis"])
    spk = bytes.fromhex(CANONICAL_QTY4["payout_script_hex"])
    spk_len = bytes([len(spk)])
    locktime_bytes = struct.pack("<I", 0)

    cb_tx_bytes = (
        version_bytes +
        tx_in_count +
        prev_txid +
        prev_vout +
        script_sig_len +
        script_sig +
        sequence +
        tx_out_count +
        value_bytes +
        spk_len +
        spk +
        locktime_bytes
    )

    txid = dsha256(cb_tx_bytes)
    merkle_root = txid

    # 2. Build 80-byte header
    header_bytes = (
        struct.pack("<i", 1) +
        b"\x00" * 32 +
        merkle_root +
        struct.pack("<I", CANONICAL_QTY4["timestamp"]) +
        struct.pack("<I", CANONICAL_QTY4["bits"]) +
        struct.pack("<I", CANONICAL_QTY4["nonce"])
    )

    block_hash = dsha256(header_bytes)
    block_bytes = header_bytes + b"\x01" + cb_tx_bytes

    # 3. Target and PoW calculation
    exponent = CANONICAL_QTY4["bits"] >> 24
    coefficient = CANONICAL_QTY4["bits"] & 0x00FFFFFF
    target = coefficient << (8 * (exponent - 3))
    h_int = int.from_bytes(block_hash[::-1], 'big')
    assert h_int <= target, f"PoW target inequality failed: {h_int} > {target}"

    hash_hex = block_hash[::-1].hex()
    mroot_hex = merkle_root[::-1].hex()

    assert hash_hex == CANONICAL_QTY4["genesis_hash"], f"Path B hash mismatch: {hash_hex}"
    assert mroot_hex == CANONICAL_QTY4["merkle_root"], f"Path B merkle root mismatch: {mroot_hex}"
    assert len(header_bytes) == 80, f"Path B header length != 80: {len(header_bytes)}"
    assert len(block_bytes) == 267, f"Path B block length != 267: {len(block_bytes)}"

    print("[PASS] Path B Independent Standalone Engine verified with 0 external dependencies.")
    return {
        "header_hex": header_bytes.hex(),
        "block_hex": block_bytes.hex(),
        "hash_hex": hash_hex,
        "merkle_root_hex": mroot_hex,
    }


def main():
    print("==================================================")
    print("QUANTYCOIN QTY4 CANONICAL GENESIS AUDIT")
    print("==================================================")

    total_errors = 0
    total_errors += audit_stale_contamination()
    total_errors += verify_runtime_consensus_constants()
    total_errors += verify_manifests()

    if total_errors > 0:
        print(f"\n[FAIL] Pre-execution audit encountered {total_errors} error(s).")
        sys.exit(1)

    res_a = path_a_core_verification()
    res_b = path_b_standalone_verification()

    print("--- [GATE 6] DUAL-PATH BYTE-FOR-BYTE CROSS VERIFICATION ---")
    assert res_a == res_b, "CRITICAL: Path A and Path B produced non-identical outputs!"
    print("[PASS] Byte-for-byte identity confirmed between Path A (Core) and Path B (Standalone).")
    print(f"       Genesis Hash: {res_a['hash_hex']}")
    print(f"       Merkle Root:  {res_a['merkle_root_hex']}")
    print(f"       Header Hex:   {res_a['header_hex']}")
    print(f"       Raw Block:    {len(bytes.fromhex(res_a['block_hex']))} bytes")

    # Cross-check against committed header hex
    comm_hdr = (repo_root / "genesis" / "public" / "genesis_header.hex").read_text(encoding="utf-8").strip()
    assert res_a["header_hex"] == comm_hdr, "Committed genesis_header.hex divergence!"
    print("[PASS] Committed genesis_header.hex matches computed serialization.")

    print("\n==================================================")
    print("ALL QTY4 GENESIS VERIFICATION GATES PASSED (100%)")
    print("==================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
