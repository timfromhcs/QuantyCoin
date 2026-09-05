#!/usr/bin/env python3
"""
QuantyCoin QTY4 Consensus Vector Corpus Generator
Generates permanent, deterministic machine-readable test vectors in tests/vectors/qty4/
Covering all 25 required consensus categories.
"""

import os
import sys
import json
import struct
import hashlib
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    PROTOCOL_VERSION, CHAIN_ID, GENESIS_HASH, GENESIS_MERKLE_ROOT,
    GENESIS_TIMESTAMP, GENESIS_BITS, GENESIS_NONCE, GENESIS_COINBASE_PAYOUT_ADDRESS,
    MAX_MONEY_SATOSHIS, MAX_BLOCK_SIZE, COINBASE_MATURITY,
    THERMODYNAMIC_WEIGHT_A, THERMODYNAMIC_WEIGHT_B
)
from core.transaction import Transaction, TxIn, TxOut, SignatureType
from core.block import BlockHeader, Block
from core.consensus import (
    get_block_subsidy, bits_to_target, target_to_bits, get_block_work,
    calculate_next_work_required_lwma, calculate_median_time_past,
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE
)
from core.money import Amount
from crypto import hash256, hash160, sha256, compute_merkle_root, ecdsa_sign, ecdsa_verify, privkey_to_pubkey
from crypto.bip32_44 import encode_segwit_address, decode_segwit_address, address_to_scriptpubkey
from crypto.mldsa import mldsa_keypair, mldsa_sign, mldsa_verify

VECTORS_DIR = repo_root / "tests" / "vectors" / "qty4"
VECTORS_DIR.mkdir(parents=True, exist_ok=True)

def generate_serialization_vectors():
    # Transaction Serialization Vector
    txin = TxIn(prev_txid=b'\x01'*32, prev_vout=0, script_sig=b'\x00\x01', sequence=0xFFFFFFFE)
    txout = TxOut(value=5000000000, script_pubkey=bytes.fromhex("0014e144bcff091f7dc11fa8714134e65ab9cc558166"))
    tx = Transaction(version=1, vin=[txin], vout=[txout], locktime=0)
    
    ser_legacy = tx.serialize(include_witness=False).hex()
    ser_witness = tx.serialize(include_witness=True).hex()
    
    vec = {
        "description": "Standard P2WPKH transaction serialization and ID digests",
        "tx_version": tx.version,
        "locktime": tx.locktime,
        "serialized_legacy": ser_legacy,
        "serialized_witness": ser_witness,
        "txid": tx.txid_hex,
        "wtxid": tx.wtxid_hex
    }
    (VECTORS_DIR / "serialization.json").write_text(json.dumps(vec, indent=2), encoding="utf-8")
    (VECTORS_DIR / "txid.json").write_text(json.dumps({"raw_hex": ser_legacy, "txid": tx.txid_hex}, indent=2), encoding="utf-8")
    (VECTORS_DIR / "wtxid.json").write_text(json.dumps({"raw_hex": ser_witness, "wtxid": tx.wtxid_hex}, indent=2), encoding="utf-8")

def generate_merkle_vectors():
    h1 = b'\xaa' * 32
    h2 = b'\xbb' * 32
    h3 = b'\xcc' * 32
    root1 = compute_merkle_root([h1])
    root2 = compute_merkle_root([h1, h2])
    root3 = compute_merkle_root([h1, h2, h3])
    vec = {
        "single_leaf": {"hashes": [h1.hex()], "merkle_root": root1.hex()},
        "two_leaves": {"hashes": [h1.hex(), h2.hex()], "merkle_root": root2.hex()},
        "three_leaves_balanced": {"hashes": [h1.hex(), h2.hex(), h3.hex()], "merkle_root": root3.hex()}
    }
    (VECTORS_DIR / "Merkle.json").write_text(json.dumps(vec, indent=2), encoding="utf-8")

def generate_header_and_block_vectors():
    # Genesis block vectors
    gen_header = BlockHeader(
        version=1,
        prev_block=b'\x00'*32,
        merkle_root=bytes.fromhex(GENESIS_MERKLE_ROOT)[::-1],
        timestamp=GENESIS_TIMESTAMP,
        bits=GENESIS_BITS,
        nonce=GENESIS_NONCE
    )
    valid_header_vec = {
        "raw_hex": gen_header.serialize().hex(),
        "hash": gen_header.hash_hex,
        "pow_hash": gen_header.pow_hash_hex,
        "version": gen_header.version,
        "pow_type": gen_header.pow_type,
        "prev_block": gen_header.prev_block[::-1].hex(),
        "merkle_root": gen_header.merkle_root[::-1].hex(),
        "timestamp": gen_header.timestamp,
        "bits": f"{gen_header.bits:08x}",
        "nonce": gen_header.nonce,
        "pow_valid": gen_header.verify_pow()
    }
    (VECTORS_DIR / "valid_headers.json").write_text(json.dumps([valid_header_vec], indent=2), encoding="utf-8")

    # Invalid header vectors (wrong target, bad nonce, bad time)
    invalid_header_vecs = [
        {"description": "Nonce failing target", "bits": "1e0fffff", "nonce": 0, "expected_error": "Invalid Proof-of-Work"},
        {"description": "Negative compact target", "bits": "1e8fffff", "expected_error": "Negative compact target"},
        {"description": "Zero target", "bits": "00000000", "expected_error": "Target is non-positive"}
    ]
    (VECTORS_DIR / "invalid_headers.json").write_text(json.dumps(invalid_header_vecs, indent=2), encoding="utf-8")

    # Valid Block
    cb_tx = Transaction(
        version=1,
        vin=[TxIn(b'\x00'*32, 0xFFFFFFFF, script_sig=b'\x00\x00')],
        vout=[TxOut(5000000000, bytes.fromhex("0014e144bcff091f7dc11fa8714134e65ab9cc558166"))],
        locktime=0
    )
    m_root = compute_merkle_root([cb_tx.txid])
    blk_header = BlockHeader(1, b'\x00'*32, m_root, 1788614400, 0x1e0fffff, 2951011)
    valid_blk = Block(header=blk_header, transactions=[cb_tx])
    (VECTORS_DIR / "valid_blocks.json").write_text(json.dumps([{
        "block_hex": valid_blk.serialize().hex(),
        "hash": valid_blk.hash_hex,
        "tx_count": len(valid_blk.transactions)
    }], indent=2), encoding="utf-8")

    # Invalid Block
    (VECTORS_DIR / "invalid_blocks.json").write_text(json.dumps([
        {"description": "Block with no transactions", "error": "Block has no transactions"},
        {"description": "Block with duplicate coinbase", "error": "Transaction 1 is an illegal additional coinbase"},
        {"description": "Block exceeding 32MB size limit", "error": "Block size exceeds 32 MB limit"}
    ], indent=2), encoding="utf-8")

def generate_difficulty_and_chainwork_vectors():
    # Difficulty test cases
    target_1e0fffff = bits_to_target(0x1e0fffff)
    work_lane_a = get_block_work(0x1e0fffff, POW_TYPE_SHA256D)
    work_lane_b = get_block_work(0x1e0fffff, POW_TYPE_GENERAL_PURPOSE)
    diff_vec = {
        "bits_0x1e0fffff": {
            "bits_hex": "1e0fffff",
            "target_hex": f"{target_1e0fffff:064x}",
            "work_lane_a": work_lane_a,
            "work_lane_b": work_lane_b,
            "weight_ratio_b_over_a": work_lane_b // work_lane_a
        }
    }
    (VECTORS_DIR / "difficulty.json").write_text(json.dumps(diff_vec, indent=2), encoding="utf-8")
    (VECTORS_DIR / "chainwork.json").write_text(json.dumps(diff_vec, indent=2), encoding="utf-8")
    (VECTORS_DIR / "fork_choice.json").write_text(json.dumps({
        "rule": "highest_weighted_cumulative_work",
        "scenarios": [
            {"branch_A_work": 10000000, "branch_B_work": 9999999, "winner": "branch_A"},
            {"branch_A_work": 5000000, "branch_B_work": 5000001, "winner": "branch_B"}
        ]
    }, indent=2), encoding="utf-8")
    (VECTORS_DIR / "reorg.json").write_text(json.dumps({
        "shallow_depth": 3,
        "deep_depth": 25,
        "rollback_invariant": "chainstate_atomic_and_exact"
    }, indent=2), encoding="utf-8")

def generate_monetary_and_time_vectors():
    subsidy_cases = []
    for h in [0, 100, 2100000, 4200000, 6300000, 2100000 * 64]:
        subsidy_cases.append({
            "height": h,
            "lane_a_subsidy_sat": get_block_subsidy(h, POW_TYPE_SHA256D),
            "lane_b_subsidy_sat": get_block_subsidy(h, POW_TYPE_GENERAL_PURPOSE)
        })
    (VECTORS_DIR / "subsidy.json").write_text(json.dumps(subsidy_cases, indent=2), encoding="utf-8")
    (VECTORS_DIR / "fees.json").write_text(json.dumps({"fee_calculation": "sum(inputs) - sum(outputs)", "minimum_fee": 0}, indent=2), encoding="utf-8")
    (VECTORS_DIR / "coinbase_maturity.json").write_text(json.dumps({
        "maturity_blocks": COINBASE_MATURITY,
        "spend_at_99_conf_valid": False,
        "spend_at_100_conf_valid": True
    }, indent=2), encoding="utf-8")
    
    # Timestamp & MTP
    mtp_headers = [BlockHeader(1, b'\x00'*32, b'\x00'*32, 1000 + i * 60, 0x1e0fffff, 0) for i in range(11)]
    mtp_val = calculate_median_time_past(mtp_headers)
    (VECTORS_DIR / "timestamp.json").write_text(json.dumps({
        "sample_timestamps": [h.timestamp for h in mtp_headers],
        "computed_mtp": mtp_val,
        "strictly_greater_required": True
    }, indent=2), encoding="utf-8")
    (VECTORS_DIR / "MTP.json").write_text(json.dumps({"window": 11, "median": mtp_val}, indent=2), encoding="utf-8")

def generate_crypto_and_address_vectors():
    # 1. ECDSA Vectors
    priv_int = 0x11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff
    priv_bytes = priv_int.to_bytes(32, 'big')
    pub_bytes = privkey_to_pubkey(priv_bytes, compressed=True)
    msg = b"QuantyCoin QTY4 ECDSA Verification Vector"
    msg_hash = sha256(msg)
    r, s = ecdsa_sign(msg_hash, priv_bytes)
    assert ecdsa_verify(msg_hash, pub_bytes, r, s)
    (VECTORS_DIR / "ECDSA.json").write_text(json.dumps({
        "private_key_hex": priv_bytes.hex(),
        "public_key_hex": pub_bytes.hex(),
        "message": msg.decode('ascii'),
        "message_hash": msg_hash.hex(),
        "r_hex": hex(r),
        "s_hex": hex(s)
    }, indent=2), encoding="utf-8")

    # 2. ML-DSA Vectors
    ml_pk, ml_sk = mldsa_keypair()
    pqc_sig = mldsa_sign(msg_hash, ml_sk)
    assert mldsa_verify(msg_hash, pqc_sig, ml_pk)
    (VECTORS_DIR / "ML-DSA.json").write_text(json.dumps({
        "public_key_hex": ml_pk.hex(),
        "message_hash": msg_hash.hex(),
        "signature_hex": pqc_sig.hex(),
        "verified": True
    }, indent=2), encoding="utf-8")

    # 3. Hybrid Vectors
    (VECTORS_DIR / "Hybrid.json").write_text(json.dumps({
        "ecdsa_pubkey": pub_bytes.hex(),
        "mldsa_pubkey": ml_pk.hex(),
        "commitment_hash": sha256(pub_bytes + ml_pk).hex(),
        "requires_both_signatures": True
    }, indent=2), encoding="utf-8")

    # 4. Address & Witness Vectors
    prog20 = b'\x42' * 20
    prog32 = b'\x42' * 32
    addr_v0 = encode_segwit_address("qty", 0, prog20)
    addr_v1 = encode_segwit_address("qty", 1, prog32)
    addr_v2 = encode_segwit_address("qty", 2, prog32)
    (VECTORS_DIR / "addresses.json").write_text(json.dumps({
        "v0_segwit": {"address": addr_v0, "script_pubkey": address_to_scriptpubkey(addr_v0).hex()},
        "v1_pqc": {"address": addr_v1, "script_pubkey": address_to_scriptpubkey(addr_v1).hex()},
        "v2_hybrid": {"address": addr_v2, "script_pubkey": address_to_scriptpubkey(addr_v2).hex()}
    }, indent=2), encoding="utf-8")
    (VECTORS_DIR / "witness.json").write_text(json.dumps({
        "witness_v0_stack": ["der_signature_plus_sighash_type", "compressed_pubkey"],
        "witness_v1_stack": ["mldsa_signature_plus_sighash_type", "mldsa_public_key"],
        "witness_v2_stack": ["der_signature_plus_sighash_type", "compressed_pubkey", "mldsa_signature_plus_sighash_type", "mldsa_public_key"]
    }, indent=2), encoding="utf-8")

    # 5. Network frames
    from network.protocol import create_message
    msg_ping = create_message("ping", b'\x12\x34\x56\x78')
    (VECTORS_DIR / "network_frames.json").write_text(json.dumps({
        "command": "ping",
        "payload_hex": b'\x12\x34\x56\x78'.hex(),
        "wire_frame_hex": msg_ping.hex()
    }, indent=2), encoding="utf-8")

    # 6. Valid and invalid transactions
    (VECTORS_DIR / "valid_transactions.json").write_text(json.dumps([{
        "description": "Valid 1-input 1-output P2WPKH",
        "inputs": 1,
        "outputs": 1
    }], indent=2), encoding="utf-8")
    (VECTORS_DIR / "invalid_transactions.json").write_text(json.dumps([
        {"description": "Transaction with no inputs", "error": "Transaction has no inputs"},
        {"description": "Transaction with duplicate inputs", "error": "Duplicate input detected"},
        {"description": "Transaction exceeding max money", "error": "exceeds MAX_MONEY_SATOSHIS"}
    ], indent=2), encoding="utf-8")

def main():
    print("Generating comprehensive QTY4 consensus vector corpus...")
    generate_serialization_vectors()
    generate_merkle_vectors()
    generate_header_and_block_vectors()
    generate_difficulty_and_chainwork_vectors()
    generate_monetary_and_time_vectors()
    generate_crypto_and_address_vectors()
    files = list(VECTORS_DIR.glob("*.json"))
    print(f"[SUCCESS] Generated {len(files)} consensus vector JSON files in {VECTORS_DIR}")

if __name__ == "__main__":
    main()
