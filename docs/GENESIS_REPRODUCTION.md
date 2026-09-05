# QuantyCoin QTY4 Genesis Block Reproduction Guide

**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Consensus Root**: Genesis Block Hash `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`  

---

## 1. Overview & Fair-Launch Principles

The QuantyCoin QTY4 Genesis Block was constructed and mined under strict fair-launch conditions:
- **100% Public Parameters**: All parameters (timestamp, headline message, payout address, target bits) are public and non-confidential.
- **Zero Creator Premine**: The genesis block coinbase reward (50 QTY) is assigned to a public community address `qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf`. No private key exists.
- **Dual-Path Independent Verification**: Two completely isolated code paths independently construct, serialize, and verify the genesis block, ensuring zero hidden state.

---

## 2. Frozen Genesis Parameters

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Protocol Version** | `70040` | Upper 16 bits = 0 (`pow_type = SHA256D`), Lower 16 bits = 70040 |
| **Timestamp** | `1788614400` | 2026-09-05 13:20:00 UTC |
| **Bits (Compact Target)** | `0x1e0fffff` | Initial mining target (`0x00000ffff...`) |
| **Nonce** | `2951011` | Proof-of-Work solution |
| **Public Headline** | `2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol` | Encoded into coinbase scriptSig |
| **Genesis Payout Address** | `qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf` | Deterministic witness v0 community address |
| **Genesis Hash** | `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3` | Double SHA-256 over 80-byte header |
| **Merkle Root** | `3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea` | Single coinbase transaction hash |
| **Total Block Size** | `267 bytes` | Canonical raw byte length |

---

## 3. Dual-Path Verification Execution

To independently verify that the genesis block is mathematically valid and identical across implementations, execute:

```bash
python scripts/verify_qty4_genesis_dual_path.py
```

### Verification Methodology:
- **Path 1 (Core Consensus Engine)**: Uses the node's native `core.block.Block`, `core.transaction.Transaction`, and `crypto.compute_merkle_root` modules to deserialize, build Merkle root, and evaluate PoW hash.
- **Path 2 (Zero-Dependency Standalone)**: Uses raw `struct.pack` and `hashlib.sha256` in complete isolation with zero imports from `core/`.
- Both paths verify:
  1. Header serialization matches byte-for-byte (`genesis/public/genesis_header.hex`).
  2. Transaction serialization matches byte-for-byte.
  3. Merkle root matches byte-for-byte (`genesis/public/genesis_merkle_root.txt`).
  4. Header hash satisfies the target `000004eb1e117df3... <= 00000ffff...`.

---

## 4. Standalone Reproduction Script (Standard Library Only)

Anyone can verify the genesis block using standard Python 3 with zero dependencies:

```python
import hashlib
import struct

def dsha256(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

# 1. Build Coinbase Transaction
version_bytes = struct.pack("<i", 1)
tx_in_count = b"\x01"
prev_txid = b"\x00" * 32
prev_vout = struct.pack("<I", 0xFFFFFFFF)

timestamp_str = "2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol"
ts_bytes = timestamp_str.encode("utf-8")
script_sig = b"\x04\xff\xff\x00\x1d\x01\x04" + bytes([len(ts_bytes)]) + ts_bytes
script_sig_len = bytes([len(script_sig)])
sequence = struct.pack("<I", 0xFFFFFFFF)

tx_out_count = b"\x01"
value_bytes = struct.pack("<q", 5000000000)
spk = bytes.fromhex("0014e144bcff091f7dc11fa8714134e65ab9cc558166")
spk_len = bytes([len(spk)])
locktime_bytes = struct.pack("<I", 0)

cb_tx_bytes = (
    version_bytes + tx_in_count + prev_txid + prev_vout +
    script_sig_len + script_sig + sequence +
    tx_out_count + value_bytes + spk_len + spk + locktime_bytes
)

txid = dsha256(cb_tx_bytes)
merkle_root = txid

# 2. Build 80-byte Header
header_bytes = (
    struct.pack("<i", 1) +
    b"\x00" * 32 +
    merkle_root +
    struct.pack("<I", 1788614400) +
    struct.pack("<I", 0x1e0fffff) +
    struct.pack("<I", 2951011)
)

block_hash = dsha256(header_bytes)
hash_hex = block_hash[::-1].hex()

assert hash_hex == "000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3"
print(f"Genesis Verified: {hash_hex}")
```
