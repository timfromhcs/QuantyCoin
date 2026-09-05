# QuantyCoin Consensus Assurance & Invariant Proofs

**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Consensus Engine**: Dual-PoW (Lane A SHA-256D ASIC & Lane B Scrypt CPU/GPU)  
**Standard**: Strict Integer Consensus Invariants, Zero-Float Arithmetic  

---

## 1. Zero Floating-Point Arithmetic Invariant

### A. The Core Problem
In distributed consensus systems, IEEE-754 floating-point arithmetic introduces non-deterministic behavior across CPU architectures, compiler optimization levels, and rounding modes. A consensus state machine that uses floating-point values will inevitably fork across platforms.

### B. The QuantyCoin QTY4 Solution
QuantyCoin enforces **zero floating-point operations** across all consensus code paths:
- All monetary amounts are represented as 64-bit unsigned integers in Satoshis (`1 QTY = 100,000,000 Satoshis`).
- The `Amount` class in [`core/money.py`](../core/money.py) encapsulates all monetary transactions with checked arithmetic:
  - Bounds enforcement: `0 <= amount <= MAX_MONEY_SATOSHIS (2,100,000,000,000,000)`.
  - Checked addition: `Amount(a) + Amount(b)` asserts `a + b <= MAX_MONEY`.
  - Checked subtraction: `Amount(a) - Amount(b)` asserts `a >= b` (no underflow).
  - Checked multiplication: Integer multiplier only.
  - Checked division: Integer floor division (`//`) and right bitwise shift (`>>`). Floating-point division (`/`) is strictly prohibited.

```python
# Subsidy Calculation (Zero-Float Bitwise Integer Shift)
def get_block_subsidy(height: int, pow_type: int = 0) -> int:
    halvings = height // HALVING_INTERVAL
    if halvings >= 64:
        return 0
    base = INITIAL_REWARD_LANE_A if pow_type == 0 else INITIAL_REWARD_LANE_B
    return base >> halvings
```

---

## 2. Strict Compact Target Decoding

In Bitcoin and derivative codebases, naive compact target decoding (e.g., `mantissa * 256**(exponent - 3)`) can accept negative targets if the mantissa sign bit is set, or produce zero if the mantissa is zero.

QuantyCoin QTY4 enforces strict compact target validation in [`core/consensus.py`](../core/consensus.py):
1. **Negative Bit Rejection**: If `mantissa & 0x00800000 != 0`, target is strictly invalid.
2. **Zero Target Rejection**: If `mantissa == 0`, target is rejected.
3. **Exponent Boundaries**: Exponents outside `[3, 34]` or producing values `> POW_LIMIT` are rejected.
4. **Exact PoW Limit Comparison**: The decoded target integer must satisfy `0 < target <= POW_LIMIT`.

---

## 3. Independent Per-Lane LWMA-1 Retargeting

Difficulty adjusts independently for Lane A (SHA-256D) and Lane B (Scrypt 1024/1/1) using the Linear-Weighted Moving Average (LWMA-1) algorithm:
- Window size: $N = 45$ blocks per lane.
- Target block spacing: $T = 120$ seconds per lane (60 seconds combined).
- Weighting sum: $S = \sum_{i=1}^N i = \frac{N(N+1)}{2} = 1035$.
- Time difference clamping: Each per-block interval $\Delta t_i$ is clamped to $[-6T, +6T] = [-720, +720]$ seconds to neutralize timewarp attacks.
- Solvetimes sum: $L = \sum_{i=1}^N (i \cdot \Delta t_i)$. Clamped to $[S \cdot T / 4, S \cdot T \cdot 4]$.
- Next Target calculation uses purely integer arithmetic:
  $$\text{NextTarget} = \left( \frac{\sum_{i=1}^N \text{Target}_i}{N} \cdot L \right) // (S \cdot T)$$

---

## 4. Cumulative Thermodynamic Chainwork

Fork choice resolution is strictly determined by cumulative thermodynamic chainwork, preventing low-difficulty GPU grinding attacks from overcoming the ASIC chain:
- Lane A (SHA-256D ASIC): Weight $W_A = 1$
- Lane B (Scrypt 1024 CPU/GPU): Weight $W_B = 2048$
- Work per block:
  $$\text{Work} = \left( \frac{2^{256}}{\text{Target} + 1} \right) \cdot W_{\text{lane}}$$
- Chainwork is the cumulative 256-bit unsigned integer sum:
  $$\text{Chainwork} = \sum_{i=0}^{\text{Tip}} \text{Work}_i$$
- When two competing valid branches exist, the node selects the tip with strictly greater cumulative chainwork.

---

## 5. Formal 12-Stage Validation Pipeline

Every candidate block must traverse the 12-stage validation pipeline in [`core/validation.py`](../core/validation.py):

| Stage | Name | Invariant Checked |
| :---: | :--- | :--- |
| **1** | `CheckBlockStructure` | 80-byte header, non-empty transactions, serialized size <= 32 MB |
| **2** | `CheckPoW` | Header hash <= decoded target, target <= POW_LIMIT |
| **3** | `CheckTimestamp` | Timestamp <= MTP + 2 hours (no drift into future) |
| **4** | `CheckCoinbase` | Exactly one coinbase at index 0, non-coinbase transactions have inputs |
| **5** | `CheckMerkleRoot` | Computed transaction Merkle root == header Merkle root |
| **6** | `CheckMedianTimePast` | Block timestamp > MTP of previous 11 blocks |
| **7** | `CheckDifficulty` | Header bits == expected LWMA-1 retarget bits |
| **8** | `CheckDuplicateTx` | Zero duplicate TxIDs within block |
| **9** | `CheckMoney` | Sum of inputs >= sum of outputs; total block fees >= 0 |
| **10**| `CheckSubsidy` | Coinbase output value <= block subsidy + total fees |
| **11**| `CheckCoinbaseMaturity` | Coinbase inputs spent only after 100 confirmation blocks |
| **12**| `CheckWitnessAndScripts`| FIPS 204 ML-DSA-44 or Secp256k1 signature validation; fail-closed |

---

## 6. Verification Evidence

All consensus invariants are verified by the automated test suite:
- [`tests/test_core.py`](../tests/test_core.py): Tests `Amount` arithmetic, subsidy halving, Merkle root.
- [`tests/test_adversarial_qty4.py`](../tests/test_adversarial_qty4.py): Tests negative target bits, integer overflows, corrupted headers, and double-spending.
- [`tests/test_dualpow_security_simulation.py`](../tests/test_dualpow_security_simulation.py): Tests lane disappearance, anti-grinding, and thermodynamic fork choice.
