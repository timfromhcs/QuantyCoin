#!/usr/bin/env python3
"""
QuantyCoin 2.0 (QTY2) Public Genesis Verification Tool
Independently verifies genesis block parameters, Merkle root, PoW difficulty target,
and serialization without requiring any private secret vault.
"""
import sys
import json
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    GENESIS_HASH,
    GENESIS_MERKLE_ROOT,
    GENESIS_TIMESTAMP,
    GENESIS_BITS,
    GENESIS_NONCE,
    GENESIS_COINBASE_PAYOUT_ADDRESS,
    GENESIS_BLOCK_REWARD,
    PROTOCOL_VERSION,
    CHAIN_ID,
    MAGIC_BYTES,
)
from core.block import Block, BlockHeader
from core.transaction import Transaction, TxIn, TxOut
from crypto.hash import hash256
from node.chainstate import Chainstate

def verify_manifest(manifest_path: Path) -> bool:
    if not manifest_path.exists():
        print(f"[FAIL] Manifest file missing: {manifest_path}")
        return False
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        g_data = data.get("genesis_block", data)
        ghash = g_data.get("hash") or g_data.get("genesis_hash")
        mroot = g_data.get("merkle_root")
        tstamp = g_data.get("timestamp")
        nonce = g_data.get("nonce")
        bits = g_data.get("bits")

        assert ghash == GENESIS_HASH, f"Genesis hash mismatch: {ghash} != {GENESIS_HASH}"
        assert mroot == GENESIS_MERKLE_ROOT, f"Merkle root mismatch: {mroot} != {GENESIS_MERKLE_ROOT}"
        assert tstamp == GENESIS_TIMESTAMP, f"Timestamp mismatch: {tstamp} != {GENESIS_TIMESTAMP}"
        assert nonce == GENESIS_NONCE, f"Nonce mismatch: {nonce} != {GENESIS_NONCE}"
        assert bits == GENESIS_BITS, f"Bits mismatch: {bits} != {GENESIS_BITS}"
        print(f"[PASS] Manifest validated: {manifest_path.name}")
        return True
    except Exception as e:
        print(f"[FAIL] Manifest validation error: {e}")
        return False

def verify_genesis_consensus():
    print("==================================================")
    print("QTY2 INDEPENDENT GENESIS CRYPTOGRAPHIC AUDIT")
    print("==================================================")
    
    # 1. Manifest checks
    m1 = repo_root / "genesis" / "PUBLIC_GENESIS_MANIFEST.json"
    m2 = repo_root / "public_genesis.json"
    if not (verify_manifest(m1) and verify_manifest(m2)):
        sys.exit(1)

    import tempfile, shutil
    temp_dir = tempfile.mkdtemp(prefix="qty2_genesis_verify_")
    try:
        # 2. Runtime Chainstate Genesis Assertions
        cs = Chainstate(datadir=temp_dir)
        assert cs.best_tip is not None, "Chainstate best_tip is None"
        tip_hash = cs.best_tip.header.hash_hex
        tip_height = cs.best_tip.height
        assert tip_hash == GENESIS_HASH, f"Chainstate genesis mismatch: {tip_hash} != {GENESIS_HASH}"
        assert tip_height == 0, f"Chainstate genesis height mismatch: {tip_height} != 0"
        print("[PASS] Chainstate genesis assertions verified.")
    except Exception as e:
        print(f"[FAIL] Chainstate genesis validation failed: {e}")
        sys.exit(1)

    # 3. Cryptographic PoW and Merkle Audit
    try:
        assert cs.best_tip is not None, "Failed to retrieve genesis block node from Chainstate"
        genesis_block, _ = Block.deserialize(cs.best_tip.raw_block)
        assert genesis_block.header.hash_hex == GENESIS_HASH, "Block header hash mismatch"
        assert genesis_block.header.verify_pow(), "Genesis block fails PoW target check"
        assert genesis_block.verify_merkle_root(), "Genesis block fails Merkle root check"
        assert genesis_block.header.merkle_root[::-1].hex() == GENESIS_MERKLE_ROOT, "Merkle root constant mismatch"
        assert genesis_block.header.nonce == GENESIS_NONCE, "Nonce mismatch"
        assert genesis_block.header.bits == GENESIS_BITS, "Bits mismatch"
        assert genesis_block.header.timestamp == GENESIS_TIMESTAMP, "Timestamp mismatch"
        print("[PASS] Block header PoW & Merkle root calculation verified.")
        print(f"       Genesis Hash: {GENESIS_HASH}")
        print(f"       Merkle Root:  {GENESIS_MERKLE_ROOT}")
        print(f"       Difficulty:   {hex(GENESIS_BITS)}")
    except Exception as e:
        print(f"[FAIL] Cryptographic PoW verification error: {e}")
        sys.exit(1)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n==================================================")
    print("GENESIS INDEPENDENT AUDIT PASSED WITH 100% SUCCESS")
    print("==================================================")
    sys.exit(0)

if __name__ == "__main__":
    verify_genesis_consensus()
