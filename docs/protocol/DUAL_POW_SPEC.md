# QuantyCoin Protocol Specification: Dual Proof-of-Work Architecture

**Document**: `DUAL_POW_SPEC.md`  
**Protocol Layer**: Consensus Layer-1 Mining & Proof-of-Work Validation  
**Status**: **DRAFT SPECIFICATION — FROZEN FOR IMPLEMENTATION**  

---

## 1. Architectural Motivation & Principles

QuantyCoin implements an independent **Dual Proof-of-Work** mining architecture designed to balance industrial ASIC security with broad consumer decentralization:

1. **Lane A (`SHA256D_ASIC`)**: High-security, industrial ASIC mining lane providing deep thermodynamic finality and energy-backed network security using standard double-SHA256 hashing.
2. **Lane B (`GENERAL_PURPOSE`)**: Accessible CPU and GPU mining lane utilizing standard, memory-hard Scrypt hashing ($N=1024, r=1, p=1$). Provides lower barrier-to-entry, community participation, and geographic distribution.

Both lanes are first-class consensus participants capable of independently advancing the blockchain if the other lane experiences sudden hashpower cessation.

---

## 2. Block Header Encoding & Lane Identification

To maintain 100% hardware compatibility with existing SHA-256D ASIC hashing pipelines and standard pool infrastructure, QuantyCoin preserves the canonical **80-byte block header format**:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Base Version (16)        |          PoW Type (16)        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                     Previous Block Hash (32)                  +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                       Merkle Root (32)                        +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Timestamp (4)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Bits (4)                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            Nonce (4)                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 2.1 Header Field Definitions
- `version` (int32, 4 bytes):
  - Bits 0..15 (`version & 0xFFFF`): Base Protocol Version (`2`).
  - Bits 16..31 (`(version >> 16) & 0xFFFF`): `pow_type` identifier:
    - `0x0000`: `POW_TYPE_SHA256D` (Lane A)
    - `0x0001`: `POW_TYPE_GENERAL_PURPOSE` (Lane B)
- `prev_block` (32 bytes): Tip hash of previous block.
- `merkle_root` (32 bytes): Cryptographic Merkle tree root of transactions.
- `timestamp` (uint32, 4 bytes): Block generation time.
- `bits` (uint32, 4 bytes): Compact representation of target difficulty for this specific lane.
- `nonce` (uint32, 4 bytes): 32-bit nonce space.

---

## 3. Proof-of-Work Verification Functions

### 3.1 Lane A: `SHA256D_ASIC`
- **Algorithm**: Standard double-SHA256.
  $$\text{PoW\_Hash}_A(H) = \text{SHA256}(\text{SHA256}(H))$$
- **Verification Condition**:
  $$\text{int.from\_bytes}(\text{PoW\_Hash}_A(H)[::-1], \text{'big'}) \le \text{bits\_to\_target}(H.\text{bits})$$

### 3.2 Lane B: `GENERAL_PURPOSE`
- **Algorithm**: RFC 7914 Scrypt with parameters:
  - $N = 1024$ (CPU/GPU memory hardness: 128 KB buffer)
  - $r = 1$
  - $p = 1$
  - $\text{Salt} = \text{"quantycoin\_pow\_gp"}$
  - $\text{Key Length} = 32\text{ bytes}$
  $$\text{PoW\_Hash}_B(H) = \text{scrypt}(H, \text{salt}=\text{"quantycoin\_pow\_gp"}, N=1024, r=1, p=1, \text{dklen}=32)$$
- **Verification Condition**:
  $$\text{int.from\_bytes}(\text{PoW\_Hash}_B(H)[::-1], \text{'big'}) \le \text{bits\_to\_target}(H.\text{bits})$$

---

## 4. Independent Per-Lane Difficulty Retargeting

To prevent hashpower changes in one lane from destabilizing the other lane, difficulty adjustment is **strictly partitioned**:

- **Target Spacing**:
  - Combined network target: $T_{\text{net}} = 60\text{ seconds}$.
  - Lane A target spacing: $T_A = 120\text{ seconds}$ ($2 \times T_{\text{net}}$).
  - Lane B target spacing: $T_B = 120\text{ seconds}$ ($2 \times T_{\text{net}}$).
- **Partitioned Histories**:
  - When calculating difficulty for a candidate Lane A block, only previous Lane A blocks are fed into the LWMA-1 window ($N=45$).
  - When calculating difficulty for a candidate Lane B block, only previous Lane B blocks are fed into the LWMA-1 window ($N=45$).
- **Failover Liveness Guarantee**:
  - If Lane A produces no blocks, the elapsed time between Lane B blocks stabilizes to 60 seconds as Lane B's LWMA retargets to absorb network demand.
  - If Lane B produces no blocks, Lane A similarly retargets to maintain chain progression.
  - Both lanes operating at design capacity yield an interleaved 60-second average block time.

---

## 5. Dual Monetary Subsidy & Hard Cap Invariant

To preserve the mathematically finite 21,000,000 QTY supply cap while rewarding the higher energy expenditure of ASIC mining:

### 5.1 Base Subsidy
At height $H$, the base network subsidy is:
$$\text{Subsidy}_{\text{base}}(H) = \left\lfloor \frac{50 \times 10^8}{2^{\lfloor H / 2,100,000 \rfloor}} \right\rfloor \text{ Satoshis}$$

### 5.2 Lane-Specific Subsidy Allocation
- **Lane A (`SHA256D_ASIC`)**: Receives 100% of base subsidy:
  $$\text{Reward}_A(H) = \text{Subsidy}_{\text{base}}(H)$$
- **Lane B (`GENERAL_PURPOSE`)**: Receives 50% of base subsidy:
  $$\text{Reward}_B(H) = \left\lfloor 0.5 \times \text{Subsidy}_{\text{base}}(H) \right\rfloor$$

### 5.3 Mathematical Supply Proof
$$\text{Max Supply} = \sum_{B \in \text{Chain}} \text{Reward}(B) \le \sum_{H=0}^{\infty} \text{Subsidy}_{\text{base}}(H) = 21,000,000\text{ QTY}$$
Because $\text{Reward}_B(H) < \text{Subsidy}_{\text{base}}(H)$, total issued coins will strictly satisfy:
$$\text{Total Issuance} \le 21,000,000\text{ QTY}$$
The hard cap can never be exceeded regardless of the ratio of Lane A to Lane B blocks.
