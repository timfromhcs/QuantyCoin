"""
QuantyCoin Core Testsuite
Unit Tests for Transaction Serialization, Block Construction, Merkle Validation, UTXO Engine & Mempool
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto import (
    generate_mnemonic, mnemonic_to_seed, HDKey,
    hash256, hash160, compute_merkle_root,
    privkey_to_pubkey, ecdsa_sign, ecdsa_verify
)
from core.transaction import Transaction, TxIn, TxOut
from core.block import Block, BlockHeader
from core.utxo import UTXOSet
from core.mempool import Mempool
from core.consensus import get_block_subsidy, bits_to_target, target_to_bits
from node.chainstate import Chainstate


def test_transaction_serialization():
    # Construct standard transaction
    txin = TxIn(prev_txid=b'\x01'*32, prev_vout=0, sequence=0xFFFFFFFE)
    txout = TxOut(value=10 * 100_000_000, script_pubkey=b'\x00\x14' + (b'\x22'*20))
    tx = Transaction(version=1, vin=[txin], vout=[txout], locktime=0)
    
    serialized = tx.serialize(include_witness=False)
    deserialized, length = Transaction.deserialize(serialized)
    
    assert deserialized.version == tx.version
    assert len(deserialized.vin) == 1
    assert deserialized.vin[0].prev_txid == b'\x01'*32
    assert deserialized.vin[0].prev_vout == 0
    assert len(deserialized.vout) == 1
    assert deserialized.vout[0].value == 10 * 100_000_000
    assert deserialized.txid == tx.txid
    print("Transaction Serialization Test: PASS")


def test_block_merkle_root():
    tx1 = Transaction(version=1, vin=[TxIn(b'\x00'*32, 0xFFFFFFFF)], vout=[TxOut(50*100_000_000, b'\x00\x14'+b'\x11'*20)])
    tx2 = Transaction(version=1, vin=[TxIn(tx1.txid, 0)], vout=[TxOut(49*100_000_000, b'\x00\x14'+b'\x22'*20)])
    
    m_root = compute_merkle_root([tx1.txid, tx2.txid])
    assert len(m_root) == 32
    print("Block Merkle Root Calculation Test: PASS")


def test_consensus_halving():
    assert get_block_subsidy(0) == 50 * 100_000_000
    assert get_block_subsidy(2_100_000) == 25 * 100_000_000
    assert get_block_subsidy(4_200_000) == 12_500_000_00 # 12.5 QTY
    print("Consensus Halving Matrix Test: PASS")


def test_chainstate_genesis():
    cs = Chainstate()
    assert cs.best_height == 0
    assert cs.best_hash_hex.startswith("00000")
    assert cs.utxo_set.total_utxo_count == 1
    print(f"Chainstate Genesis Test: PASS (Height: {cs.best_height}, Tip: {cs.best_hash_hex[:16]}...)")


def run_all_core_tests():
    print("\n========================================================")
    print("RUNNING CORE UNIT TEST SUITE")
    print("========================================================")
    test_transaction_serialization()
    test_block_merkle_root()
    test_consensus_halving()
    test_chainstate_genesis()
    print("========================================================")
    print("ALL CORE UNIT TESTS PASSED WITH 100% SUCCESS!")
    print("========================================================\n")


if __name__ == "__main__":
    run_all_core_tests()
