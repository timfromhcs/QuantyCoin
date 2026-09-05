# QuantyCoin QTY4 Weighted Cumulative Work Specification

**Protocol**: QTY4 (70040)  
**Consensus Role**: Authoritative Fork-Choice Rule  

---

## 1. Thermodynamic Work Definition

In an asymmetric dual-PoW blockchain, raw block count conveys zero economic security. Fork-choice resolution must strictly evaluate **Weighted Cumulative Work** committed to each branch.

For a block with target $T$ on mining lane $L$:
$$\text{RawWork}(T) = \left\lfloor \frac{2^{256}}{T + 1} \right\rfloor$$

$$\text{LaneWork}(L, T) = W_L \times \text{RawWork}(T)$$

Where:
- $W_A = 1$ for Lane A (Double SHA-256 ASIC).
- $W_B = 2048$ for Lane B (Scrypt 1024 CPU/GPU, calibrated to 1024 memory iterations).

---

## 2. Chain Cumulative Work

The cumulative chainwork $\mathcal{W}(C)$ of chain $C$ from genesis to tip is:
$$\mathcal{W}(C) = \sum_{B \in C} \text{LaneWork}(B.\text{pow\_type}, \text{target}(B.\text{bits}))$$

---

## 3. Fork Choice Invariant

When evaluating competing tips $C_1$ and $C_2$:
1. If $\mathcal{W}(C_1) > \mathcal{W}(C_2)$, select $C_1$ as the active best tip.
2. If $\mathcal{W}(C_2) > \mathcal{W}(C_1)$, select $C_2$ as the active best tip.
3. If $\mathcal{W}(C_1) == \mathcal{W}(C_2)$, retain the tip first received (first-seen rule).

### Anti-Grinding Security Guarantee
Because $W_B = 2048$ normalizes Scrypt memory work to physical thermodynamic commitment, an attacker attempting to create a long chain of low-difficulty blocks on Lane B cannot overtake an honest chain with higher cumulative energy commitment.
