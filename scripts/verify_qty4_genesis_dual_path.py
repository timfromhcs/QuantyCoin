#!/usr/bin/env python3
"""
QuantyCoin QTY4 Genesis Block Dual-Path Independent Verifier & Artifact Generator.
Path 1: QuantyCoin Core Engine (core.block, core.transaction)
Path 2: Pure Standalone Python Engine (zero project dependencies, only standard library)
"""

import sys
import json
import struct
import hashlib
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

# Immutable Frozen Genesis Parameters
PARAMS = {
    "protocol_version": 70040,
    "chain_id": "quantycoin-4.0",
    "timestamp_str": "2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol",
    "timestamp": 1788614400,
    "bits": 0x1e0fffff,
    "nonce": 2951011,
    "reward_satoshis": 5000000000,
    "payout_address": "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf",
    "payout_script_hex": "0014e144bcff091f7dc11fa8714134e65ab9cc558166",
    "expected_genesis_hash": "000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3",
    "expected_merkle_root": "3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea"
}

def path1_core_verification():
    """Path 1: Verify using core codebase modules."""
    from core.transaction import Transaction, TxIn, TxOut
    from core.block import BlockHeader, Block
    from crypto import compute_merkle_root

    script_sig = (
        b'\x04\xff\xff\x00\x1d\x01\x04' +
        bytes([len(PARAMS["timestamp_str"])]) +
        PARAMS["timestamp_str"].encode('utf-8')
    )
    spk = bytes.fromhex(PARAMS["payout_script_hex"])
    cb_tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=PARAMS["reward_satoshis"], script_pubkey=spk)],
        locktime=0
    )
    merkle_root = compute_merkle_root([cb_tx.txid])
    header = BlockHeader(
        version=1,
        prev_block=b'\x00' * 32,
        merkle_root=merkle_root,
        timestamp=PARAMS["timestamp"],
        bits=PARAMS["bits"],
        nonce=PARAMS["nonce"]
    )
    block = Block(header=header, transactions=[cb_tx])
    
    res = {
        "header_hex": header.serialize().hex(),
        "block_hex": block.serialize().hex(),
        "hash_hex": header.hash_hex,
        "merkle_root_hex": merkle_root[::-1].hex(),
        "pow_valid": header.verify_pow()
    }
    return res

def path2_standalone_verification():
    """Path 2: Pure standalone reimplementation without importing any project modules."""
    def dsha256(b: bytes) -> bytes:
        return hashlib.sha256(hashlib.sha256(b).digest()).digest()

    # Build coinbase tx manually
    version_bytes = struct.pack("<i", 1)
    tx_in_count = b"\x01"
    prev_txid = b"\x00" * 32
    prev_vout = struct.pack("<I", 0xFFFFFFFF)
    
    ts_bytes = PARAMS["timestamp_str"].encode('utf-8')
    script_sig = b"\x04\xff\xff\x00\x1d\x01\x04" + bytes([len(ts_bytes)]) + ts_bytes
    script_sig_len = bytes([len(script_sig)])
    sequence = struct.pack("<I", 0xFFFFFFFF)
    
    tx_out_count = b"\x01"
    value_bytes = struct.pack("<q", PARAMS["reward_satoshis"])
    spk = bytes.fromhex(PARAMS["payout_script_hex"])
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
    
    # TxID is double SHA256 of tx bytes
    txid = dsha256(cb_tx_bytes)
    # Merkle root of single tx is txid
    merkle_root = txid
    
    # Build 80-byte header
    header_bytes = (
        struct.pack("<i", 1) +
        b"\x00" * 32 +
        merkle_root +
        struct.pack("<I", PARAMS["timestamp"]) +
        struct.pack("<I", PARAMS["bits"]) +
        struct.pack("<I", PARAMS["nonce"])
    )
    
    block_hash = dsha256(header_bytes)
    block_bytes = header_bytes + b"\x01" + cb_tx_bytes
    
    # Check PoW target
    exponent = PARAMS["bits"] >> 24
    coefficient = PARAMS["bits"] & 0x00FFFFFF
    target = coefficient << (8 * (exponent - 3))
    h_int = int.from_bytes(block_hash[::-1], 'big')
    pow_valid = (h_int <= target)
    
    res = {
        "header_hex": header_bytes.hex(),
        "block_hex": block_bytes.hex(),
        "hash_hex": block_hash[::-1].hex(),
        "merkle_root_hex": merkle_root[::-1].hex(),
        "pow_valid": pow_valid
    }
    return res

def export_artifacts(res1, res2):
    assert res1 == res2, "Divergence detected between verification paths!"
    assert res1["hash_hex"] == PARAMS["expected_genesis_hash"], "Genesis hash mismatch!"
    assert res1["merkle_root_hex"] == PARAMS["expected_merkle_root"], "Merkle root mismatch!"
    assert res1["pow_valid"], "PoW verification failed!"

    pub_dir = repo_root / "genesis" / "public"
    pub_dir.mkdir(parents=True, exist_ok=True)

    # 1. genesis_hash.txt
    (pub_dir / "genesis_hash.txt").write_text(res1["hash_hex"] + "\n", encoding="utf-8")
    # 2. genesis_merkle_root.txt
    (pub_dir / "genesis_merkle_root.txt").write_text(res1["merkle_root_hex"] + "\n", encoding="utf-8")
    # 3. genesis_header.hex
    (pub_dir / "genesis_header.hex").write_text(res1["header_hex"] + "\n", encoding="utf-8")
    # 4. genesis_parameters.json
    (pub_dir / "genesis_parameters.json").write_text(json.dumps(PARAMS, indent=2) + "\n", encoding="utf-8")
    # 5. genesis_block.json
    block_dict = {
        "hash": res1["hash_hex"],
        "merkle_root": res1["merkle_root_hex"],
        "header_hex": res1["header_hex"],
        "block_hex": res1["block_hex"],
        "timestamp": PARAMS["timestamp"],
        "timestamp_str": PARAMS["timestamp_str"],
        "bits": f"{PARAMS['bits']:08x}",
        "nonce": PARAMS["nonce"],
        "reward_satoshis": PARAMS["reward_satoshis"],
        "payout_address": PARAMS["payout_address"],
        "payout_script_hex": PARAMS["payout_script_hex"]
    }
    (pub_dir / "genesis_block.json").write_text(json.dumps(block_dict, indent=2) + "\n", encoding="utf-8")

    # 6. public_genesis_manifest.json
    manifest = {
        "protocol_version": PARAMS["protocol_version"],
        "chain_id": PARAMS["chain_id"],
        "genesis_hash": res1["hash_hex"],
        "merkle_root": res1["merkle_root_hex"],
        "timestamp": PARAMS["timestamp"],
        "bits": PARAMS["bits"],
        "nonce": PARAMS["nonce"],
        "serialized_genesis_block": res1["block_hex"],
        "serialized_genesis_header": res1["header_hex"],
        "network_magic": "0x51545934",
        "verification_state": "INDEPENDENTLY_VERIFIED_DUAL_PATH"
    }
    (pub_dir / "public_genesis_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Also update genesis/PUBLIC_GENESIS_MANIFEST.json
    (repo_root / "genesis" / "PUBLIC_GENESIS_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # 7. README.md
    readme_content = f"""# QuantyCoin QTY4 Public Genesis Block

**Chain Identifier**: `{PARAMS['chain_id']}`  
**Protocol Version**: `{PARAMS['protocol_version']}`  
**Genesis Block Hash**: `{res1['hash_hex']}`  
**Merkle Root**: `{res1['merkle_root_hex']}`  

---

## Public Consensus Inputs

- **Timestamp String**: `"{PARAMS['timestamp_str']}"`
- **Unix Timestamp**: `{PARAMS['timestamp']}`
- **Target Bits**: `0x{PARAMS['bits']:08x}`
- **Winning Nonce**: `{PARAMS['nonce']}`
- **Coinbase Payout Address**: `{PARAMS['payout_address']}`
- **Coinbase ScriptPubKey**: `{PARAMS['payout_script_hex']}`
- **Coinbase Reward**: `50 QTY` ({PARAMS['reward_satoshis']} satoshis)

---

## Independent Reproducibility & Dual-Path Verification

This Genesis Block is 100% publicly reproducible without accessing any private key or generation secret.
To verify with both Path 1 (Core engine) and Path 2 (Zero-dependency standalone Python):

```bash
python scripts/verify_qty4_genesis_dual_path.py
```

Both independent paths produce identical byte-level serializations, hashes, and Merkle roots.
"""
    (pub_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # Also update spec/qty4/genesis.json
    (repo_root / "spec" / "qty4" / "genesis.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("\n[SUCCESS] Both verification paths matched with 100% byte-for-byte identity!")
    print(f"Genesis Hash: {res1['hash_hex']}")
    print(f"Merkle Root:  {res1['merkle_root_hex']}")
    print(f"All 7 public artifacts written to genesis/public/ and spec/qty4/genesis.json.")

if __name__ == "__main__":
    print("Running Path 1: Core Engine Verification...")
    res1 = path1_core_verification()
    print("Running Path 2: Standalone Engine Verification...")
    res2 = path2_standalone_verification()
    export_artifacts(res1, res2)
