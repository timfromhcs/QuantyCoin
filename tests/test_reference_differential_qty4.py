"""
QTY4 production-vs-reference differential test.

Compares core/ production implementation against reference/qty4_reference.py
/stdlib-only independent implementation across deterministic vectors:
compact targets, work, subsidy/halving boundaries, money range, MTP,
varint, merkle/txid, header serialization, segwit addresses, fork choice.
"""

import struct
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core import consensus as P
from core import genesis_constants as G
from core.block import BlockHeader
from crypto import hash256
from crypto.bip32_44 import decode_segwit_address
from reference import qty4_reference as R


class TestReferenceDifferential(unittest.TestCase):
    def test_compact_roundtrip(self):
        vectors = [0x1E0FFFFF, 0x1D00FFFF, 0x1B0404CB, 0x1E00FFFF, 0x01123456, 0x02123456]
        for bits in vectors:
            try:
                pt = P.bits_to_target(bits)
            except ValueError:
                with self.assertRaises(ValueError):
                    R.compact_to_target(bits)
                continue
            rt = R.compact_to_target(bits)
            self.assertEqual(pt, rt, f"target mismatch bits=0x{bits:08x}")
            self.assertEqual(P.target_to_bits(pt), R.target_to_compact(rt))

    def test_compact_rejects_negative(self):
        for bad in (0x1E800000, 0x1E8FFFFF, 0x1D800001):
            with self.assertRaises(ValueError):
                P.bits_to_target(bad)
            with self.assertRaises(ValueError):
                R.compact_to_target(bad)

    def test_work_agreement(self):
        for bits in (0x1E0FFFFF, 0x1D00FFFF, 0x1B0404CB):
            for lane, rlane in ((P.POW_TYPE_SHA256D, R.LANE_A),
                                (P.POW_TYPE_GENERAL_PURPOSE, R.LANE_B)):
                self.assertEqual(P.get_block_work(bits, lane), R.block_work(bits, rlane))

    def test_subsidy_boundaries(self):
        H = G.SUBSIDY_HALVING_INTERVAL
        for h in (0, 1, H - 1, H, H + 1, 2 * H, 2 * H + 1, 64 * H, 64 * H + 5):
            for lane, rlane in ((P.POW_TYPE_SHA256D, R.LANE_A),
                                (P.POW_TYPE_GENERAL_PURPOSE, R.LANE_B)):
                self.assertEqual(P.get_block_subsidy(h, lane), R.block_subsidy(h, rlane), f"h={h}")

    def test_money_range(self):
        for v in (0, 1, G.MAX_MONEY_SATOSHIS, G.MAX_MONEY_SATOSHIS + 1, -1):
            self.assertEqual(P.check_money_range(v), R.check_money_range(v))

    def test_mtp(self):
        stamps = [1788614400 + 60 * i for i in range(20)]
        self.assertEqual(P.calculate_median_time_past(
            [type("H", (), {"timestamp": t})() for t in stamps]), R.median_time_past(stamps))
        self.assertEqual(R.median_time_past([]), 0)

    def test_header_serialization(self):
        hdr = BlockHeader(1, b"\x11" * 32, b"\x22" * 32, 1788614400, 0x1E0FFFFF, 7)
        raw = hdr.serialize()
        ref_raw = R.serialize_header(1, b"\x11" * 32, b"\x22" * 32, 1788614400, 0x1E0FFFFF, 7)
        self.assertEqual(raw, ref_raw)
        fields, n = R.deserialize_header(raw)
        self.assertEqual(n, 80)
        self.assertEqual(fields["bits"], 0x1E0FFFFF)
        self.assertEqual(R.header_hash(raw), hash256(raw))

    def test_merkle_and_txid(self):
        from core.transaction import Transaction, TxIn, TxOut
        tx = Transaction(version=1, vin=[TxIn(b"\x00" * 32, 0xFFFFFFFF)],
                         vout=[TxOut(5000000000, b"\x00\x14" + b"\x99" * 20)])
        txid_prod = tx.txid
        ref_txid = R.hash256(tx.serialize(include_witness=False))
        self.assertEqual(txid_prod, ref_txid)
        self.assertEqual(R.merkle_root([ref_txid]), ref_txid)

    def test_address_decode(self):
        addr = "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf"
        pv, pp = decode_segwit_address("qty", addr)
        rv, rp = R.segwit_decode("qty", addr)
        self.assertEqual(pv, rv)
        self.assertEqual(pp, rp)
        for bad in (addr[:-1] + ("a" if addr[-1] != "a" else "b"), addr.upper().replace("QTY", "BTC")):
            _, pp2 = decode_segwit_address("qty", bad)
            rv2, rp2 = R.segwit_decode("qty", bad)
            self.assertIsNone(pp2)
            self.assertIsNone(rp2)

    def test_fork_choice_tiebreak(self):
        self.assertEqual(R.select_tip(10, 100, 9, 200), "b")
        self.assertEqual(R.select_tip(10, 300, 9, 200), "a")
        self.assertEqual(R.select_tip(10, 100, 12, 100), "b")


if __name__ == "__main__":
    unittest.main()
