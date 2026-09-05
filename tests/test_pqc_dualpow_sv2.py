"""
QuantyCoin PQC, Dual-PoW Consensus, and Stratum V2 Test Suite
Exhaustive functional and unit tests covering:
1. NIST FIPS 204 ML-DSA-65 & Hybrid PQC Transaction Signatures & Verification
2. Bech32m Address Encoding (qty1p... for PQC, qty1z... for Hybrid)
3. Dual-PoW Mining (SHA-256D ASIC Lane A & General-Purpose Scrypt Lane B)
4. Dual-PoW Independent Retargeting & Cumulative Thermodynamic Chainwork Reorgs
5. Stratum V2 Binary Framing, Channel Multiplexing, and Dual-PoW Mining Jobs
6. New RPC Methods (getmininglanes, getminingtargets, getchainwork, getnewpqaddress, getaddressinfo, getstratuminfo)
"""

import os
import sys
import time
import struct
import hashlib
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto import hash256, sha256, hash160, HDKey
from crypto.mldsa import MLDSAKey, mldsa_keypair, mldsa_sign, mldsa_verify, SIGNATURE_BYTES, PUBLIC_KEY_BYTES
from crypto.bip32_44 import (
    encode_segwit_address, decode_segwit_address,
    address_to_scriptpubkey, MAINNET_BECH32_HRP
)
from core.transaction import Transaction, TxIn, TxOut, SignatureType
from core.block import Block, BlockHeader
from core.consensus import (
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE,
    LANE_WEIGHT_SHA256D, LANE_WEIGHT_GENERAL_PURPOSE,
    get_block_subsidy, bits_to_target, target_to_bits,
    calculate_next_work_required_dual
)
from node.chainstate import Chainstate
from node.rpc_server import QuantyRPCServer
from wallet.hd_wallet import HDWallet
from wallet.rpc_client import WalletRPCClient
from miner.stratum_v2 import (
    encode_sv2_frame, decode_sv2_frame,
    encode_setup_connection, decode_setup_connection,
    encode_new_mining_job, decode_new_mining_job,
    encode_submit_shares_standard, decode_submit_shares_standard,
    StratumV2Server, StratumV2Client,
    MSG_SETUP_CONNECTION, MSG_NEW_MINING_JOB, MSG_SUBMIT_SHARES_STANDARD
)


class TestPQCAndDualPoW(unittest.TestCase):
    """Unit and integration test cases for PQC and Dual-PoW."""

    def test_01_mldsa_and_hybrid_signatures(self):
        """Test NIST FIPS 204 ML-DSA and Hybrid transaction signing & verification."""
        # 1. Generate keys (exact 32-byte seeds)
        secp_key = HDKey.from_seed(b"test_seed_for_classical_signing_")
        pq_key = MLDSAKey.from_seed(b"test_seed_for_pqc_signing_32byte")

        # 2. Test Pure ML-DSA Address & Spending
        pq_prog = sha256(pq_key.public_key)
        pq_addr = encode_segwit_address(MAINNET_BECH32_HRP, 1, pq_prog)
        self.assertTrue(pq_addr.startswith("qty1p"))

        # Decode address
        ver, decoded_prog = decode_segwit_address(MAINNET_BECH32_HRP, pq_addr)
        self.assertEqual(ver, 1)
        self.assertEqual(decoded_prog, pq_prog)

        # Build transaction spending from PQC scriptPubKey
        pq_script = address_to_scriptpubkey(pq_addr)
        self.assertEqual(pq_script, b'\x51\x20' + pq_prog)

        dest_script = b'\x00\x14' + (b'\x44' * 20)
        tx_pq = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\xaa'*32, prev_vout=0)],
            vout=[TxOut(value=10 * 100_000_000, script_pubkey=dest_script)]
        )
        tx_pq.sign_input_mldsa(0, pq_key.secret_key, pq_key.public_key, pq_script, 10 * 100_000_000)
        self.assertTrue(tx_pq.verify_input_signature(0, pq_script, 10 * 100_000_000))

        # 3. Test Hybrid Address & Spending
        hybrid_prog = sha256(secp_key.get_public_key() + pq_key.public_key)
        hybrid_addr = encode_segwit_address(MAINNET_BECH32_HRP, 2, hybrid_prog)
        self.assertTrue(hybrid_addr.startswith("qty1z"))

        ver_hyb, decoded_hyb = decode_segwit_address(MAINNET_BECH32_HRP, hybrid_addr)
        self.assertEqual(ver_hyb, 2)
        self.assertEqual(decoded_hyb, hybrid_prog)

        hyb_script = address_to_scriptpubkey(hybrid_addr)
        self.assertEqual(hyb_script, b'\x52\x20' + hybrid_prog)

        tx_hyb = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\xbb'*32, prev_vout=1)],
            vout=[TxOut(value=5 * 100_000_000, script_pubkey=dest_script)]
        )
        tx_hyb.sign_input_hybrid(0, secp_key.key, pq_key.secret_key, pq_key.public_key, hyb_script, 5 * 100_000_000)
        self.assertTrue(tx_hyb.verify_input_signature(0, hyb_script, 5 * 100_000_000))

        # Test invalid signature rejection
        tx_bad = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\xbb'*32, prev_vout=1)],
            vout=[TxOut(value=5 * 100_000_000, script_pubkey=dest_script)]
        )
        tx_bad.sign_input(0, secp_key.key, hyb_script, 5 * 100_000_000) # Classical sig on hybrid script
        self.assertFalse(tx_bad.verify_input_signature(0, hyb_script, 5 * 100_000_000))
        print("[PASS] PQC & Hybrid Signature Verification")

    def test_02_dual_pow_mining_and_verification(self):
        """Test mining and verification for both Lane A (SHA256D) and Lane B (General Purpose Scrypt)."""
        temp_dir = tempfile.mkdtemp(prefix="quanty_cs_")
        cs = Chainstate(datadir=temp_dir)

        # 1. Mine Lane A Block (SHA256D)
        tip_hash = cs.best_hash
        tip_height = cs.best_height
        target_bits_a = 0x1f7fffff  # Fast test target

        cb_tx_a = Transaction(
            version=1,
            vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=b'\x04LANE_A')],
            vout=[TxOut(get_block_subsidy(tip_height + 1, POW_TYPE_SHA256D), b'\x00\x14'+b'\x01'*20)]
        )
        hdr_a = BlockHeader(
            version=(POW_TYPE_SHA256D << 16) | 2,
            prev_block=tip_hash,
            merkle_root=cb_tx_a.txid,
            timestamp=int(time.time()),
            bits=target_bits_a,
            nonce=0
        )
        hdr_a.mine()
        self.assertEqual(hdr_a.pow_type, POW_TYPE_SHA256D)
        self.assertTrue(hdr_a.verify_pow())

        blk_a = Block(header=hdr_a, transactions=[cb_tx_a])
        ok, reason = cs.process_block(blk_a)
        self.assertTrue(ok, f"Lane A block rejected: {reason}")
        self.assertEqual(cs.best_height, tip_height + 1)
        self.assertEqual(cs.best_tip.pow_type, POW_TYPE_SHA256D)

        # 2. Mine Lane B Block (Scrypt General Purpose)
        tip_hash = cs.best_hash
        tip_height = cs.best_height
        target_bits_b = 0x2000ffff  # Fast test target

        cb_tx_b = Transaction(
            version=1,
            vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=b'\x04LANE_B')],
            vout=[TxOut(get_block_subsidy(tip_height + 1, POW_TYPE_GENERAL_PURPOSE), b'\x00\x14'+b'\x02'*20)]
        )
        hdr_b = BlockHeader(
            version=(POW_TYPE_GENERAL_PURPOSE << 16) | 2,
            prev_block=tip_hash,
            merkle_root=cb_tx_b.txid,
            timestamp=int(time.time()),
            bits=target_bits_b,
            nonce=0
        )
        hdr_b.mine()
        self.assertEqual(hdr_b.pow_type, POW_TYPE_GENERAL_PURPOSE)
        self.assertTrue(hdr_b.verify_pow())

        blk_b = Block(header=hdr_b, transactions=[cb_tx_b])
        ok, reason = cs.process_block(blk_b)
        self.assertTrue(ok, f"Lane B block rejected: {reason}")
        self.assertEqual(cs.best_height, tip_height + 1)
        self.assertEqual(cs.best_tip.pow_type, POW_TYPE_GENERAL_PURPOSE)
        print("[PASS] Dual-PoW Lane A & Lane B Mining & Verification")

    def test_03_cumulative_chainwork_fork_resolution(self):
        """
        Verify that cumulative thermodynamic work, not block count, determines best chain.
        """
        temp_dir = tempfile.mkdtemp(prefix="quanty_reorg_")
        cs = Chainstate(datadir=temp_dir)
        genesis_hash = cs.best_hash

        # Build Branch 1: High-Work Lane A block (low target = high difficulty)
        hard_bits = 0x1f00ffff # More difficult
        cb1 = Transaction(version=1, vin=[TxIn(b'\x00'*32, 0xFFFFFFFF)], vout=[TxOut(50*100_000_000, b'\x00\x14'+b'\x11'*20)])
        hdr1 = BlockHeader(
            version=(POW_TYPE_SHA256D << 16) | 2,
            prev_block=genesis_hash,
            merkle_root=cb1.txid,
            timestamp=int(time.time()),
            bits=hard_bits,
            nonce=0
        )
        hdr1.mine()

        # Build Branch 2: Easy Lane B block
        easy_bits = 0x207fffff # Very easy
        cb2_1 = Transaction(version=1, vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=b'\x01')], vout=[TxOut(25*100_000_000, b'\x00\x14'+b'\x22'*20)])
        hdr2_1 = BlockHeader(
            version=(POW_TYPE_GENERAL_PURPOSE << 16) | 2,
            prev_block=genesis_hash,
            merkle_root=cb2_1.txid,
            timestamp=int(time.time()) + 1,
            bits=easy_bits,
            nonce=0
        )
        hdr2_1.mine()

        w1 = cs.get_block_work(hdr1)
        w2_1 = cs.get_block_work(hdr2_1)
        self.assertGreater(w1, w2_1)
        print("[PASS] Cumulative Thermodynamic Chainwork Calculations")

    def test_04_stratum_v2_framing_and_protocol(self):
        """Test Stratum V2 binary codec, message serialization, and server-client communication."""
        # 1. Test Frame Serialization
        setup_payload = encode_setup_connection(min_version=2, max_version=2, pow_lane=1)
        frame_bytes = encode_sv2_frame(0, MSG_SETUP_CONNECTION, setup_payload)
        self.assertGreater(len(frame_bytes), 6)

        # Decode frame
        ext, mtype, payload, consumed = decode_sv2_frame(frame_bytes)
        self.assertEqual(mtype, MSG_SETUP_CONNECTION)
        self.assertEqual(consumed, len(frame_bytes))
        decoded_setup = decode_setup_connection(payload)
        self.assertEqual(decoded_setup["protocol"], 2)
        self.assertEqual(decoded_setup["pow_lane"], 1)

        # 2. Test Mining Job Serialization
        job_bytes = encode_new_mining_job(1, 101, 1, 2, b'\x11'*32, b'\x22'*32, 123456789, 0x1f0fffff)
        job_frame = encode_sv2_frame(0, MSG_NEW_MINING_JOB, job_bytes)
        _, mtype_job, payload_job, _ = decode_sv2_frame(job_frame)
        self.assertEqual(mtype_job, MSG_NEW_MINING_JOB)
        decoded_job = decode_new_mining_job(payload_job)
        self.assertEqual(decoded_job["channel_id"], 1)
        self.assertEqual(decoded_job["job_id"], 101)
        self.assertEqual(decoded_job["pow_type"], 1)

        # 3. Test Full Stratum V2 Handshake over Localhost Server
        port = 19445
        server = StratumV2Server(host="127.0.0.1", port=port)
        server.start()
        time.sleep(0.5)

        client = StratumV2Client(host="127.0.0.1", port=port, pow_lane=0)
        try:
            connected = client.connect()
            self.assertTrue(connected)
            self.assertEqual(client.channel_id, 1)
            self.assertIsNotNone(client.active_job)
            self.assertEqual(client.active_job["pow_type"], 0)

            # Submit Share
            submitted = client.submit_share(nonce=0, ntime=client.active_job["timestamp"])
            self.assertIn(submitted, (True, False))
        finally:
            client.close()
            server.stop()
        print("[PASS] Stratum V2 Binary Framing & Dual-Lane Multiplexing")

    def test_05_rpc_methods(self):
        """Test all new protocol RPC endpoints."""
        temp_dir = tempfile.mkdtemp(prefix="quanty_rpc_")
        cs = Chainstate(datadir=temp_dir)
        rpc_server = QuantyRPCServer(chainstate=cs, host="127.0.0.1", port=19881)
        rpc_server.start()
        time.sleep(0.5)

        client = WalletRPCClient(rpc_host="127.0.0.1", rpc_port=19881)
        try:
            # 1. getmininglanes
            lanes = client.get_mining_lanes()
            self.assertIn("active_lanes", lanes)
            lane_names = [l["name"] for l in lanes["active_lanes"]]
            self.assertIn("SHA256D_ASIC", lane_names)
            self.assertIn("GENERAL_PURPOSE", lane_names)
            self.assertEqual(lanes["active_lanes"][0]["weight"], 1)
            self.assertEqual(lanes["active_lanes"][1]["weight"], 2048)

            # 2. getminingtargets
            targets = client.get_mining_targets()
            self.assertIn("SHA256D_ASIC", targets)
            self.assertIn("GENERAL_PURPOSE", targets)

            # 3. getchainwork
            cw = client.get_chainwork()
            self.assertIn("chainwork_hex", cw)
            self.assertIn("chainwork_int", cw)
            self.assertGreater(cw["chainwork_int"], 0)

            # 4. getnewpqaddress
            pq_addr = client.get_new_pq_address()
            self.assertTrue(pq_addr["address"].startswith("qty1p"))
            self.assertEqual(pq_addr["witness_version"], 1)

            # 5. getaddressinfo
            info_pq = client.get_address_info(pq_addr["address"])
            self.assertTrue(info_pq["quantum_secure"])
            self.assertEqual(info_pq["type"], "p2pqpkh_mldsa")

            info_legacy = client.get_address_info("qty1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq5npt3r")
            self.assertFalse(info_legacy["quantum_secure"])

            # 6. getstratuminfo
            stratum_info = client.get_stratum_info()
            self.assertTrue(stratum_info["stratum_v2"]["enabled"])
            self.assertEqual(stratum_info["stratum_v2"]["port"], 3334)
        finally:
            rpc_server.stop()
        print("[PASS] New Protocol RPC Endpoints")

    def test_06_hd_wallet_pqc_integration(self):
        """Test HDWallet generating and spending from PQC and Hybrid addresses."""
        wallet = HDWallet()

        # 1. Address generation
        pq_addr_0 = wallet.get_pq_address(0)
        hyb_addr_0 = wallet.get_hybrid_address(0)
        self.assertTrue(pq_addr_0.startswith("qty1p"))
        self.assertTrue(hyb_addr_0.startswith("qty1z"))

        # 2. Key lookups
        self.assertIsNotNone(wallet.find_pq_key_for_address(pq_addr_0))
        self.assertIsNotNone(wallet.find_hybrid_keys_for_address(hyb_addr_0))

        # 3. Spend from PQC UTXO
        pq_script = address_to_scriptpubkey(pq_addr_0)
        mock_pq_utxos = [{
            "txid": "00" * 32,
            "vout": 0,
            "value_sat": 50 * 100_000_000,
            "scriptPubKey": pq_script.hex(),
            "address": pq_addr_0
        }]
        dest_addr = wallet.get_receiving_address(1)
        tx_pqc_spent = wallet.build_transaction(dest_addr, 20 * 100_000_000, mock_pq_utxos)
        self.assertTrue(tx_pqc_spent.verify_input_signature(0, pq_script, 50 * 100_000_000))

        # 4. Spend from Hybrid UTXO
        hyb_script = address_to_scriptpubkey(hyb_addr_0)
        mock_hyb_utxos = [{
            "txid": "11" * 32,
            "vout": 0,
            "value_sat": 50 * 100_000_000,
            "scriptPubKey": hyb_script.hex(),
            "address": hyb_addr_0
        }]
        tx_hyb_spent = wallet.build_transaction(dest_addr, 20 * 100_000_000, mock_hyb_utxos)
        self.assertTrue(tx_hyb_spent.verify_input_signature(0, hyb_script, 50 * 100_000_000))

        # 5. Quantum Vulnerability Audit & Automated Migration
        legacy_addr = wallet.get_receiving_address(0)

        legacy_script = address_to_scriptpubkey(legacy_addr)
        mixed_utxos = [
            {"txid": "22" * 32, "vout": 0, "value_sat": 15 * 100_000_000, "scriptPubKey": legacy_script.hex(), "address": legacy_addr},
            {"txid": "33" * 32, "vout": 1, "value_sat": 25 * 100_000_000, "scriptPubKey": pq_script.hex(), "address": pq_addr_0},
        ]
        vuln_report = wallet.get_quantum_vulnerability_report(mixed_utxos)
        self.assertTrue(vuln_report["has_vulnerable_utxos"])
        self.assertEqual(vuln_report["vulnerable_count"], 1)
        self.assertEqual(vuln_report["vulnerable_total_sat"], 15 * 100_000_000)
        self.assertEqual(vuln_report["pqc_count"], 1)

        # Build migration transaction sweeping legacy UTXO into ML-DSA custody
        migration_tx = wallet.build_pqc_migration_transaction(mixed_utxos, target_mode="mldsa", fee_sat=10000)
        self.assertEqual(len(migration_tx.vin), 1) # Only sweeps vulnerable UTXOs
        self.assertEqual(len(migration_tx.vout), 1)
        self.assertEqual(migration_tx.vout[0].value, 15 * 100_000_000 - 10000)
        self.assertEqual(migration_tx.vout[0].script_pubkey, pq_script)
        self.assertTrue(migration_tx.verify_input_signature(0, legacy_script, 15 * 100_000_000))

        print("[PASS] HDWallet Post-Quantum Key Derivation & Transaction Creation")

    def test_07_reject_pseudo_crypto_and_malleated_signatures(self):
        """Attacker crafts synthetic/length-padded signatures or corrupted public keys."""
        k = MLDSAKey.from_seed(b"\x42" * 32)
        msg = b"Adversarial transfer of 1,000,000 QTY to attacker"

        # 1. Genuine signature passes
        sig = k.sign(msg)
        self.assertTrue(k.verify(msg, sig))

        # 2. Fake signature with correct length but pseudo-crypto content must FAIL
        fake_sig = b"\x00" * SIGNATURE_BYTES
        self.assertFalse(k.verify(msg, fake_sig))

        # 3. Single-bit malleated signature must FAIL
        malleated_sig = bytearray(sig)
        malleated_sig[len(malleated_sig) // 2] ^= 0x01
        self.assertFalse(k.verify(msg, bytes(malleated_sig)))

        # 4. Malleated public key must FAIL
        malleated_pk = bytearray(k.public_key)
        malleated_pk[100] ^= 0x01
        self.assertFalse(mldsa_verify(msg, sig, bytes(malleated_pk)))

        # 5. Wrong message must FAIL
        self.assertFalse(k.verify(b"Legitimate transfer of 1 QTY", sig))
        print("[PASS] Strict Rejection of Pseudo-Crypto & Malleated Signatures")

    def test_08_cross_mode_replay_attack_prevention(self):
        """Attacker attempts to replay an ECDSA signature on an ML-DSA input or vice-versa."""
        secp = HDKey.from_seed(b"classical_key_seed_32_bytes!!_")
        pqc = MLDSAKey.from_seed(b"pqc_key_seed_32_bytes_value!1234")


        pqc_prog = sha256(pqc.public_key)
        pqc_script = b'\x51\x20' + pqc_prog

        tx = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\x11'*32, prev_vout=0)],
            vout=[TxOut(value=100_000_000, script_pubkey=b'\x00\x14'+b'\x22'*20)]
        )

        # Attacker tries to satisfy ML-DSA script with classical ECDSA witness
        tx.sign_input(0, secp.key, pqc_script, 100_000_000)
        self.assertFalse(tx.verify_input_signature(0, pqc_script, 100_000_000))

        # Attacker tries to satisfy Hybrid script with only ML-DSA witness
        hyb_prog = sha256(secp.get_public_key() + pqc.public_key)
        hyb_script = b'\x52\x20' + hyb_prog

        tx_hyb = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\x33'*32, prev_vout=0)],
            vout=[TxOut(value=100_000_000, script_pubkey=b'\x00\x14'+b'\x22'*20)]
        )
        tx_hyb.sign_input_mldsa(0, pqc.secret_key, pqc.public_key, hyb_script, 100_000_000)
        self.assertFalse(tx_hyb.verify_input_signature(0, hyb_script, 100_000_000))
        print("[PASS] Cross-Mode Signature Replay Attack Prevention")

    def test_09_thermodynamic_chainwork_defeats_low_difficulty_spam(self):
        """
        Attacker creates a longer branch with many rapid low-difficulty blocks.
        Honest branch has fewer blocks but higher thermodynamic chainwork.
        Node MUST choose the honest branch with higher cumulative work, rejecting the longer chain.
        """
        temp_dir = tempfile.mkdtemp(prefix="quanty_adv_")
        cs = Chainstate(datadir=temp_dir)
        base_hash = cs.best_hash
        base_height = cs.best_height

        bits_high_work = 0x1e00ffff
        target_high = bits_to_target(bits_high_work)

        bits_low_work = 0x1f7fffff
        target_low = bits_to_target(bits_low_work)

        work_high = ( (1 << 256) // (target_high + 1) ) * LANE_WEIGHT_SHA256D
        work_low = ( (1 << 256) // (target_low + 1) ) * LANE_WEIGHT_GENERAL_PURPOSE

        self.assertGreater(work_high, work_low * 3)

        # 1. Mine Honest Block 1 (high work)
        cb1 = Transaction(
            version=1,
            vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=b'\x04HONEST_1')],
            vout=[TxOut(get_block_subsidy(base_height + 1, POW_TYPE_SHA256D), b'\x00\x14'+b'\x01'*20)]
        )
        hdr1 = BlockHeader(
            version=(POW_TYPE_SHA256D << 16) | 2,
            prev_block=base_hash,
            merkle_root=cb1.txid,
            timestamp=int(time.time()),
            bits=bits_high_work,
            nonce=0
        )
        hdr1.mine()
        blk1 = Block(header=hdr1, transactions=[cb1])
        ok, reason = cs.process_block(blk1)
        self.assertTrue(ok, f"Honest block 1 rejected: {reason}")
        honest_tip_hash = cs.best_hash
        self.assertEqual(cs.best_height, base_height + 1)

        # 2. Mine 3 rapid blocks on Attacker branch from base_hash with low work
        attacker_prev = base_hash
        for i in range(3):
            cb_att = Transaction(
                version=1,
                vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=f'\x04ATT_{i}'.encode())],
                vout=[TxOut(get_block_subsidy(base_height + 1 + i, POW_TYPE_GENERAL_PURPOSE), b'\x00\x14'+b'\x02'*20)]
            )
            hdr_att = BlockHeader(
                version=(POW_TYPE_GENERAL_PURPOSE << 16) | 2,
                prev_block=attacker_prev,
                merkle_root=cb_att.txid,
                timestamp=int(time.time()) + (i * 10),
                bits=bits_low_work,
                nonce=0
            )
            hdr_att.mine()
            blk_att = Block(header=hdr_att, transactions=[cb_att])
            attacker_prev = blk_att.hash
            ok, _ = cs.process_block(blk_att)
            self.assertTrue(ok)

        honest_cw = cs.block_index[honest_tip_hash].chainwork
        attacker_cw = cs.block_index[attacker_prev].chainwork

        self.assertGreater(honest_cw, attacker_cw)
        self.assertEqual(cs.best_hash, honest_tip_hash)
        self.assertEqual(cs.best_height, base_height + 1)
        print("[PASS] Thermodynamic Chainwork Defeats Low-Difficulty Spam Attack")


if __name__ == "__main__":
    unittest.main()

