# QuantyCoin QTY4 Dual Proof-of-Work Specification

**Protocol**: QTY4 (70040)  
**Consensus Architecture**: Asymmetric Dual-Lane PoW  

---

## 1. Mining Lanes & Algorithm Parameters

| Parameter | Lane A (Industrial ASIC) | Lane B (Consumer CPU/GPU) |
| :--- | :--- | :--- |
| **Identifier (`pow_type`)** | `0` (`0x0000`) | `1` (`0x0001`) |
| **Header Encoding** | `version >> 16 == 0` | `version >> 16 == 1` |
| **Algorithm** | Double SHA-256 (SHA-256D) | RFC 7914 Scrypt |
| **Scrypt Parameters** | N/A | $N=1024, r=1, p=1, dklen=32$ |
| **Scrypt Salt** | N/A | `b"quantycoin_pow_gp"` |
| **Target Block Interval** | 120 seconds | 120 seconds |
| **Weighted Work Multiplier ($W$)** | `1` ($W_A$) | `2048` ($W_B$) |
| **Base Block Subsidy** | 50 QTY (5,000,000,000 satoshis) | 25 QTY (2,500,000,000 satoshis) |
| **PoW Limit Bits** | `0x1e0fffff` | `0x1e0fffff` |
| **PoW Limit Target** | `0x000fffff...0000` | `0x000fffff...0000` |

---

## 2. Combined Network Throughput

- **Combined Nominal Interval**:
  $$\frac{1}{\frac{1}{T_A} + \frac{1}{T_B}} = \frac{1}{\frac{1}{120} + \frac{1}{120}} = 60 \text{ seconds}$$
- **Failover Liveness**: If either lane experiences a complete cessation of hashrate, the remaining lane continues to advance the chain independently. The difficulty adjustment algorithm adapts within the 45-block window.

---

## 3. Proof-of-Work Verification Function

For a candidate block header $H$:
1. Determine `pow_type = (H.version >> 16) & 0xFFFF`.
2. Compute `pow_hash`:
   - If `pow_type == 0`: $\text{pow\_hash} = \text{SHA256}(\text{SHA256}(H.\text{serialize}()))$.
   - If `pow_type == 1`: $\text{pow\_hash} = \text{scrypt}(H.\text{serialize}(), \text{salt}=\text{"quantycoin\_pow\_gp"}, N=1024, r=1, p=1)$.
   - Otherwise: Reject block immediately with `Invalid PoW Type`.
3. Interpret `pow_hash` as a little-endian unsigned 256-bit integer $h$.
4. Check condition:
   $$h \le \text{target}(H.\text{bits})$$
   If condition is not met, reject block immediately.
