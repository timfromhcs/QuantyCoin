# QuantyCoin QTY4 Canonical Binary Serialization Specification

**Protocol**: QTY4 (70040)  
**Standard**: Strict Deterministic Binary Encoding (Zero Floating-Point, Zero JSON Wire Formats)  

---

## 1. Primitive Type Serialization

All integer types are encoded in **little-endian** byte order:
- `uint8`: 1 byte unsigned integer.
- `int32`: 4 bytes signed integer (`<i`).
- `uint32`: 4 bytes unsigned integer (`<I`).
- `int64`: 8 bytes signed integer (`<q`).
- `uint64`: 8 bytes unsigned integer (`<Q`).
- `varint`: Variable-length integer encoding:
  - Value `< 0xFD`: 1 byte (`uint8`).
  - `0xFD <= Value <= 0xFFFF`: `0xFD` followed by 2 bytes (`<H`).
  - `0xFFFF < Value <= 0xFFFFFFFF`: `0xFE` followed by 4 bytes (`<I`).
  - Value `> 0xFFFFFFFF`: `0xFF` followed by 8 bytes (`<Q`).

---

## 2. Block Header Serialization (80 Bytes Exact)

| Offset | Field | Type | Size | Description |
| :--- | :--- | :--- | :--- | :--- |
| `0` | `version` | `int32` | 4 bytes | Base version (lower 16 bits) + PoW type (upper 16 bits) |
| `4` | `prev_block` | `bytes32` | 32 bytes | Double-SHA256 hash of previous block header |
| `36` | `merkle_root`| `bytes32` | 32 bytes | Merkle tree root of transactions in this block |
| `68` | `timestamp` | `uint32` | 4 bytes | Unix epoch timestamp in seconds |
| `72` | `bits` | `uint32` | 4 bytes | Compact representation of target difficulty |
| `76` | `nonce` | `uint32` | 4 bytes | Nonce value proving PoW |

---

## 3. Wire Framing Protocol (P2P Messages)

Every P2P message frame consists of a 24-byte header followed by the payload:

| Field | Type | Size | Description |
| :--- | :--- | :--- | :--- |
| `magic` | `bytes4` | 4 bytes | Network magic (`0x51545934` for mainnet) |
| `command` | `char[12]`| 12 bytes | ASCII command name, padded with trailing `0x00` bytes |
| `length` | `uint32` | 4 bytes | Payload length in bytes (max: `33,554,432`) |
| `checksum` | `bytes4` | 4 bytes | First 4 bytes of Double-SHA256(payload) |
| `payload` | `bytes` | Variable | Serialized message payload |
