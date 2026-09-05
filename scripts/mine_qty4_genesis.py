#!/usr/bin/env python3
"""
QuantyCoin QTY4 Genesis Block Miner & Multi-Path Verifier
Air-gap compliant: Uses 100% public consensus parameters and zero secrets.
"""

import sys
import struct
import hashlib
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.transaction import Transaction, TxIn, TxOut
from core.block import BlockHeader, Block
from crypto import compute_merkle_root, hash256
from crypto.bip32_44 import encode_segwit_address, address_to_scriptpubkey

# Public Genesis Parameters for QTY4
QTY4_CHAIN_ID = "quantycoin-4.0"
QTY4_PROTOCOL_VERSION = 70040
QTY4_TIMESTAMP_STR = "2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol"
QTY4_TIMESTAMP = 1788614400
QTY4_BITS = 0x1e0fffff
QTY4_REWARD_SATOSHIS = 50 * 100_000_000

# Deterministic Public Community Burn Program
COMMUNITY_SEED = b"QUANTYCOIN_QTY4_SOVEREIGN_GENESIS_COMMUNITY_2026"
PROGRAM = hashlib.new('ripemd160', hashlib.sha256(COMMUNITY_SEED).digest()).digest()
GENESIS_ADDRESS = encode_segwit_address("qty", 0, PROGRAM)
SCRIPT_PUBKEY = address_to_scriptpubkey(GENESIS_ADDRESS)

def build_coinbase_tx():
    script_sig = (
        b'\x04\xff\xff\x00\x1d\x01\x04' +
        bytes([len(QTY4_TIMESTAMP_STR)]) +
        QTY4_TIMESTAMP_STR.encode('utf-8')
    )
    tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=QTY4_REWARD_SATOSHIS, script_pubkey=SCRIPT_PUBKEY)],
        locktime=0
    )
    return tx

def mine_genesis():
    cb_tx = build_coinbase_tx()
    merkle_root = compute_merkle_root([cb_tx.txid])
    
    print(f"Mining QTY4 Genesis Block...")
    print(f"Timestamp String: {QTY4_TIMESTAMP_STR}")
    print(f"Genesis Address:  {GENESIS_ADDRESS}")
    print(f"ScriptPubKey:     {SCRIPT_PUBKEY.hex()}")
    print(f"Merkle Root:      {merkle_root[::-1].hex()}")
    
    header = BlockHeader(
        version=1,
        prev_block=b'\x00' * 32,
        merkle_root=merkle_root,
        timestamp=QTY4_TIMESTAMP,
        bits=QTY4_BITS,
        nonce=0
    )
    
    target = header.get_target()
    print(f"Target:           {target:064x}")
    
    nonce = header.mine()
    genesis_hash = header.hash_hex
    print(f"[FOUND NONCE]:    {nonce}")
    print(f"[GENESIS HASH]:   {genesis_hash}")
    
    block = Block(header=header, transactions=[cb_tx])
    valid, msg = block.validate_structure()
    assert valid, f"Block validation failed: {msg}"
    print(f"[VALIDATION]:     {msg} (PASS)")
    
    return header, block

if __name__ == "__main__":
    mine_genesis()
