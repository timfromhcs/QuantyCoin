# QuantyCoin QTY4 Difficulty Adjustment Specification (LWMA-1)

**Protocol**: QTY4 (70040)  
**Algorithm**: Linear Weighted Moving Average (LWMA-1)  
**Arithmetic**: Pure Integer Arithmetic (Zero Floating-Point Operations)  

---

## 1. Mathematical Formulation

Difficulty is adjusted independently per mining lane ($L \in \{A, B\}$) using the previous $N = 45$ blocks of that specific lane.

### Parameters
- **Window Size ($N$)**: 45 blocks.
- **Lane Target Interval ($T$)**: 120 seconds.
- **Weight Constant ($k$)**:
  $$k = \sum_{i=1}^{N} i = \frac{N(N + 1)}{2} = \frac{45 \times 46}{2} = 1035$$

### Calculation Procedure
For candidate block $H$ on lane $L$:
1. Select the last $N$ consecutive blocks on lane $L$: $B_1, B_2, \dots, B_N$ where $B_N$ is the most recent.
2. If fewer than $N$ blocks exist on lane $L$, return the default $\text{POW\_LIMIT\_BITS} = \text{0x1e0fffff}$.
3. Compute weighted solvetime sum:
   $$S = \sum_{i=1}^{N} i \times \text{clamp}(\text{timestamp}(B_i) - \text{timestamp}(B_{i-1}), -6T, 6T)$$
   where solvetime is clamped to $[-720, +720]$ seconds to neutralize timestamp manipulation attacks.
4. Calculate integer weighted target:
   $$\text{avg\_target} = \frac{1}{k} \sum_{i=1}^{N} i \times \text{target}(B_i.\text{bits})$$
   $$\text{next\_target} = \frac{\text{avg\_target} \times S}{k \times T}$$
5. Apply target clamping:
   $$\text{next\_target} = \min(\text{next\_target}, \text{POW\_LIMIT})$$
6. Encode $\text{next\_target}$ into 32-bit compact format (`bits`).
