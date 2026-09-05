# QuantyCoin QTY4 Transaction Specification

**Protocol**: QTY4 (70040)  
**Standard Version**: 2  

---

## 1. Transaction Structure

A QuantyCoin transaction consists of inputs (`vin`), outputs (`vout`), locktime, and optional witness stack data.

| Field | Type | Size | Description |
| :--- | :--- | :--- | :--- |
| `version` | `int32` | 4 bytes | Transaction version (default: 2) |
| `marker` | `uint8` | 1 byte | SegWit marker (`0x00`, only present if witness data exists) |
| `flag` | `uint8` | 1 byte | SegWit flag (`0x01`, only present if witness data exists) |
| `vin_count` | `varint` | 1–9 bytes | Number of transaction inputs |
| `vin` | `TxIn[]` | Variable | Array of transaction inputs |
| `vout_count` | `varint` | 1–9 bytes | Number of transaction outputs |
| `vout` | `TxOut[]` | Variable | Array of transaction outputs |
| `witness` | `WitnessStack[]` | Variable | Per-input witness authorization items (only if flag present) |
| `locktime` | `uint32` | 4 bytes | Block height (< 500,000,000) or Unix timestamp |

---

## 2. TxIn Structure

- `prev_txid`: 32 bytes (LE). Hash of previous transaction.
- `prev_vout`: 4 bytes uint32 (LE). Output index within previous transaction.
- `script_sig`: Varint-prefixed script bytes. Empty in native SegWit/PQC transactions.
- `sequence`: 4 bytes uint32 (LE). RBF signaling and locktime enablement (`0xFFFFFFFF` to disable).

---

## 3. TxOut Structure

- `value`: 8 bytes int64 (LE). Integer amount in satoshis ($0 \le v \le 21,000,000 \times 10^8$).
- `script_pubkey`: Varint-prefixed locking script bytes:
  - Mode 0 (SegWit v0): `0x00 0x14 [20-byte pubkey hash]`
  - Mode 1 (ML-DSA-44 v1): `0x51 0x20 [32-byte ML-DSA pubkey hash]`
  - Mode 2 (Hybrid v2): `0x52 0x20 [32-byte hybrid commitment hash]`

---

## 4. Digest Identifiers

- **TxID**: Double-SHA256 of the legacy serialization (excluding marker, flag, and witness stack).
- **WTxID**: Double-SHA256 of the complete witness serialization. For transactions without witness data, $\text{wtxid} = \text{txid}$.
