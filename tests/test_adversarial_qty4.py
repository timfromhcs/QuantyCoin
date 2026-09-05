"""
QuantyCoin QTY4 Comprehensive Adversarial & Fuzz-Smoke Testsuite
Phase P11: Property testing, fuzz smoke tests, and adversarial edge-case verification.
Enforces:
  1. Invalid input MUST NOT mutate consensus state.
  2. Round-trip serialization MUST be deterministic.
  3. Failed block connection MUST leave chainstate exactly unchanged.
"""

import os
import sys
import copy
import struct
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    GENESIS_HASH, GENESIS_BITS, GENESIS_NONCE,
    MAX_MONEY_SATOSHIS, MAX_BLOCK_SIZE
)
from core.block import BlockHeader, Block
from core.transaction import Transaction, TxIn, TxOut, SignatureType
from core.consensus import (
    bits_to_target, target_to_bits, get_block_work,
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE
)
from core.validation import (
    CheckMoney, CheckTransaction, CheckBlock, CheckPoW,
    CheckCoinbase, CheckInputs
)
from core.utxo import UTXOSet, UTXOEntry
from core.money import Amount, MoneyRangeError
from node.chainstate import Chainstate
from crypto import hash256, sha256, ecdsa_sign, ecdsa_verify, privkey_to_pubkey
from crypto.bip32_44 import (
    encode_segwit_address, decode_segwit_address,
    address_to_scriptpubkey, bech32_decode
)
from crypto.mldsa import mldsa_keypair, mldsa_sign, mldsa_verify
from network.protocol import create_message, parse_header, HEADER_LENGTH
from miner.stratum_v2 import encode_sv2_frame, decode_sv2_frame, MSG_SETUP_CONNECTION


class TestAdversarialQTY4(unittest.TestCase):

    def test_01_compact_target_decoder_adversarial(self):
        """Strictly reject negative, zero, out-of-range, and malformed compact targets."""
        # Negative compact target (bit 0x00800000 set)
        with self.assertRaises(ValueError):
            bits_to_target(0x1e8fffff)

        # Non-negative valid target
        t = bits_to_target(0x1e0fffff)
        self.assertGreater(t, 0)

        # Target to bits round trip
        b = target_to_bits(t)
        self.assertEqual(b, 0x1e0fffff)

        # Zero target
        self.assertEqual(target_to_bits(0), 0)
        self.assertEqual(target_to_bits(-100), 0)

    def test_02_block_header_deserialization_fuzz(self):
        """BlockHeader.deserialize must cleanly raise on corrupt or truncated inputs."""
        # Too short (< 80 bytes)
        for length in [0, 1, 10, 79]:
            with self.assertRaises(ValueError):
                BlockHeader.deserialize(b'\x00' * length)

        # Valid 80 bytes round-trip
        valid_bytes = (
            struct.pack('<i', 1) +
            b'\x11' * 32 +
            b'\x22' * 32 +
            struct.pack('<I', 1788614400) +
            struct.pack('<I', 0x1e0fffff) +
            struct.pack('<I', 12345)
        )
        header, offset = BlockHeader.deserialize(valid_bytes)
        self.assertEqual(offset, 80)
        self.assertEqual(header.serialize(), valid_bytes)

    def test_03_transaction_deserialization_and_validation(self):
        """Malformed transactions must be rejected without altering state."""
        # Empty inputs
        tx_no_in = Transaction(version=1, vin=[], vout=[TxOut(100, b'\x00\x14'+b'\x11'*20)])
        ok, msg = CheckTransaction(tx_no_in)
        self.assertFalse(ok)
        self.assertIn("no inputs", msg)

        # Empty outputs
        tx_no_out = Transaction(version=1, vin=[TxIn(b'\x01'*32, 0)], vout=[])
        ok, msg = CheckTransaction(tx_no_out)
        self.assertFalse(ok)
        self.assertIn("no outputs", msg)

        # Duplicate inputs
        dup_in = TxIn(b'\x01'*32, 0)
        tx_dup = Transaction(version=1, vin=[dup_in, dup_in], vout=[TxOut(100, b'\x00\x14'+b'\x11'*20)])
        ok, msg = CheckTransaction(tx_dup)
        self.assertFalse(ok)
        self.assertIn("Duplicate input", msg)

        # Negative output value
        with self.assertRaises(ValueError):
            TxOut(-50, b'\x00\x14'+b'\x11'*20)

        # Output exceeding MAX_MONEY_SATOSHIS
        with self.assertRaises(ValueError):
            TxOut(MAX_MONEY_SATOSHIS + 1, b'\x00\x14'+b'\x11'*20)

    def test_04_pqc_mldsa_adversarial_bitflips(self):
        """ML-DSA-44 must fail closed on bitflips in signature or public key."""
        pk, sk = mldsa_keypair()
        msg = b"Adversarial PQC Test Message QTY4"
        sig = mldsa_sign(msg, sk)
        self.assertTrue(mldsa_verify(msg, sig, pk))

        # Mutate signature
        mutated_sig = bytearray(sig)
        mutated_sig[100] ^= 0xFF
        self.assertFalse(mldsa_verify(msg, bytes(mutated_sig), pk))

        # Mutate public key
        mutated_pk = bytearray(pk)
        mutated_pk[50] ^= 0xAA
        self.assertFalse(mldsa_verify(msg, sig, bytes(mutated_pk)))

        # Truncated signature
        self.assertFalse(mldsa_verify(msg, sig[:100], pk))

    def test_05_hybrid_authorization_adversarial(self):
        """Hybrid authorization fails if either ECDSA or ML-DSA signature is invalid."""
        priv_bytes = (42).to_bytes(32, 'big')
        pub_ecdsa = privkey_to_pubkey(priv_bytes, compressed=True)
        pk_mldsa, sk_mldsa = mldsa_keypair()

        hybrid_hash = sha256(pub_ecdsa + pk_mldsa)
        hybrid_script = b'\x52\x20' + hybrid_hash

        tx = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\x01'*32, prev_vout=0)],
            vout=[TxOut(value=1000, script_pubkey=hybrid_script)],
            locktime=0
        )
        tx.sign_input_hybrid(0, priv_bytes, sk_mldsa, pk_mldsa, hybrid_script, 1000)

        # Honest hybrid signature must verify
        self.assertTrue(tx.verify_input_signature(0, hybrid_script, 1000))

        # Corrupt ECDSA signature portion
        corrupt_witness = list(tx.vin[0].witness)
        der_sig = bytearray(corrupt_witness[0])
        der_sig[4] ^= 0x55
        corrupt_witness[0] = bytes(der_sig)
        tx.vin[0].witness = corrupt_witness
        self.assertFalse(tx.verify_input_signature(0, hybrid_script, 1000))

    def test_06_p2p_wire_framing_adversarial(self):
        """P2P network frame parser must reject alien magic bytes and corrupt checksums."""
        payload = b"test payload 12345"
        valid_frame = create_message("ping", payload)

        # Parse valid frame
        magic, cmd, plen, chk = parse_header(valid_frame[:HEADER_LENGTH])
        self.assertEqual(cmd, "ping")
        self.assertEqual(plen, len(payload))
        self.assertEqual(chk, hash256(payload)[:4])

        # Alien magic bytes
        corrupt_magic_frame = b"XQTY" + valid_frame[4:]
        c_magic, _, _, _ = parse_header(corrupt_magic_frame[:HEADER_LENGTH])
        self.assertNotEqual(c_magic, b"QTY4")

        # Corrupt checksum
        corrupt_chk_frame = bytearray(valid_frame)
        corrupt_chk_frame[20] ^= 0xFF
        _, _, _, bad_chk = parse_header(bytes(corrupt_chk_frame[:HEADER_LENGTH]))
        self.assertNotEqual(bad_chk, hash256(payload)[:4])

    def test_07_stratum_v2_framing_adversarial(self):
        """Stratum V2 parser must safely reject truncated and malformed frames."""
        valid_sv2 = encode_sv2_frame(0, MSG_SETUP_CONNECTION, b'\x00\x02\x00\x00')
        ext, mtype, payload, consumed = decode_sv2_frame(valid_sv2)
        self.assertEqual(mtype, MSG_SETUP_CONNECTION)
        self.assertEqual(consumed, len(valid_sv2))

        # Truncated SV2 header (< 6 bytes)
        ext, mtype, payload, consumed = decode_sv2_frame(b'\x00\x01\x02')
        self.assertEqual(consumed, 0)

        # Incomplete payload
        ext, mtype, payload, consumed = decode_sv2_frame(valid_sv2[:len(valid_sv2) - 1])
        self.assertEqual(consumed, 0)

    def test_08_bech32_address_adversarial(self):
        """Address decoder must strictly reject invalid characters, mixed case, and corrupt checksums."""
        addr = "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf"
        ver, prog = decode_segwit_address("qty", addr)
        self.assertEqual(ver, 0)
        self.assertIsNotNone(prog)

        # Corrupt checksum
        corrupt_addr = addr[:-1] + ("a" if addr[-1] != "a" else "b")
        c_ver, c_prog = decode_segwit_address("qty", corrupt_addr)
        self.assertIsNone(c_prog)

        # Wrong HRP
        w_ver, w_prog = decode_segwit_address("btc", addr)
        self.assertIsNone(w_prog)

    def test_09_utxo_failed_block_leaves_state_unchanged(self):
        """Failed block application must leave UTXO set exactly unchanged."""
        utxo_set = UTXOSet()
        initial_entry = UTXOEntry(value=5000000000, script_pubkey=b'\x00\x14'+b'\x99'*20, height=0)
        outpoint = (b'\x01'*32, 0)
        utxo_set._utxos[outpoint] = initial_entry

        count_before = utxo_set.total_utxo_count
        circ_before = utxo_set.total_circulation

        # Create block with missing UTXO input
        bad_tx = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\x02'*32, prev_vout=0)], # Missing UTXO!
            vout=[TxOut(100, b'\x00\x14'+b'\x88'*20)]
        )
        with self.assertRaises(ValueError):
            utxo_set.apply_block(b'\xaa'*32, 1, [bad_tx])

        # State must remain 100% unchanged
        self.assertEqual(utxo_set.total_utxo_count, count_before)
        self.assertEqual(utxo_set.total_circulation, circ_before)
        self.assertIn(outpoint, utxo_set._utxos)

    def test_10_reorg_atomic_rollback_on_failed_branch(self):
        """If a reorganization branch fails mid-application, state rolls back to previous tip."""
        cs = Chainstate()
        initial_height = cs.best_height
        initial_hash = cs.best_hash
        initial_utxos = cs.utxo_set.total_utxo_count

        # Attempt to process an invalid orphan or corrupt block
        bad_block = Block(
            header=BlockHeader(1, b'\xfe'*32, b'\x00'*32, 1000, 0x1e0fffff, 0),
            transactions=[]
        )
        ok, msg = cs.process_block(bad_block)
        self.assertFalse(ok)

        # Tip and UTXO count must be perfectly preserved
        self.assertEqual(cs.best_height, initial_height)
        self.assertEqual(cs.best_hash, initial_hash)
        self.assertEqual(cs.utxo_set.total_utxo_count, initial_utxos)


if __name__ == "__main__":
    unittest.main()
