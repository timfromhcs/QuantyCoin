# QuantyCoin Protocol Specification: Stratum V2 Mining Protocol

**Document**: `STRATUM_V2_SPEC.md`  
**Protocol Layer**: Pool & Solo Mining Transport Protocol  
**Reference**: Stratum V2 Open Architecture Specification  
**Status**: **DRAFT SPECIFICATION — FROZEN FOR IMPLEMENTATION**  

---

## 1. Architectural Scope

This specification defines the native **Stratum V2** protocol engine for QuantyCoin, providing a high-efficiency binary transport protocol with native channel multiplexing, reduced bandwidth overhead, and explicit support for **Dual Proof-of-Work lanes** (`SHA256D_ASIC` and `GENERAL_PURPOSE`).

---

## 2. Binary Framing Architecture

All Stratum V2 messages are framed with a standard 6-byte header:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       extension_type (16)     |  msg_type (8) |   length      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    ... length (24 continued)  |        payload ...            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 2.1 Header Fields
- `extension_type` (uint16, 2 bytes): Protocol extension space (`0x0000` = Core Stratum V2 Mining Protocol).
- `msg_type` (uint8, 1 byte): Discrete message opcode.
- `length` (uint24, 3 bytes): Length of payload in bytes (maximum payload 16 MB).
- `payload`: Binary serialized message body.

---

## 3. Core Message Types & Opcodes

| Opcode (`msg_type`) | Message Name | Direction | Purpose |
| :--- | :--- | :--- | :--- |
| `0x00` | `SetupConnection` | Client &rarr; Server | Negotiates protocol version, supported features, and mining lane |
| `0x01` | `SetupConnection.Success` | Server &rarr; Client | Confirms connection and returns server identity |
| `0x02` | `SetupConnection.Error` | Server &rarr; Client | Rejects connection with error code |
| `0x10` | `OpenStandardMiningChannel` | Client &rarr; Server | Requests opening a standard downstream channel |
| `0x11` | `OpenStandardMiningChannel.Success` | Server &rarr; Client | Grants channel ID, extranonce prefix, and initial target |
| `0x12` | `OpenStandardMiningChannel.Error` | Server &rarr; Client | Rejects channel request |
| `0x13` | `OpenExtendedMiningChannel` | Client &rarr; Server | Requests opening an advanced channel (custom search space) |
| `0x14` | `OpenExtendedMiningChannel.Success`| Server &rarr; Client | Grants extended channel parameters |
| `0x20` | `SetNewPrevHash` | Server &rarr; Client | Broadcasts new tip hash on block arrival (low latency) |
| `0x21` | `NewMiningJob` | Server &rarr; Client | Distributes new candidate block template |
| `0x22` | `NewExtendedMiningJob` | Server &rarr; Client | Distributes template with custom transaction selection |
| `0x23` | `SetTarget` | Server &rarr; Client | Adjusts miner share difficulty target |
| `0x30` | `SubmitSharesStandard` | Client &rarr; Server | Submits solved share for standard channel |
| `0x31` | `SubmitSharesExtended` | Client &rarr; Server | Submits solved share for extended channel |
| `0x32` | `SubmitShares.Success` | Server &rarr; Client | Acknowledges accepted share and updates counter |
| `0x33` | `SubmitShares.Error` | Server &rarr; Client | Reports stale, duplicate, or invalid share |

---

## 4. QuantyCoin Dual-PoW Protocol Extensions

To support both ASIC and CPU/GPU mining lanes over Stratum V2, QuantyCoin extends the negotiation and channel payloads:

### 4.1 Extended `SetupConnection` Payload
- `protocol` (uint8): Protocol identifier (`0x02`).
- `min_version` (uint16): Minimum supported SV2 version (`2`).
- `max_version` (uint16): Maximum supported SV2 version (`2`).
- `flags` (uint32): Feature capability flags.
- `network` (uint32): Network magic (`0x5155414E` for Mainnet QTY2).
- **`pow_lane`** (uint8): Mining lane selection:
  - `0x00`: `SHA256D_ASIC`
  - `0x01`: `GENERAL_PURPOSE`

### 4.2 Extended `NewMiningJob` Payload
- `channel_id` (uint32): Target channel.
- `job_id` (uint32): Monotonically increasing job sequence number.
- **`pow_type`** (uint8): PoW algorithm required (`0` = SHA256D, `1` = Scrypt).
- `version` (int32): Candidate block header version field (includes lane identifier).
- `prev_hash` (32 bytes): Previous block hash.
- `merkle_root` (32 bytes): Candidate Merkle root.
- `timestamp` (uint32): Target block header time.
- **`lane_target`** (32 bytes): Full 256-bit network target for candidate block.
- **`share_target`** (32 bytes): Target required for pool share credit.
