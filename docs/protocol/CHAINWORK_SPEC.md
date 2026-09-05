# QuantyCoin Protocol Specification: Dual-PoW Cumulative Chainwork

**Document**: `CHAINWORK_SPEC.md`  
**Protocol Layer**: Consensus Fork-Choice & Cumulative Proof-of-Work Verification  
**Status**: **DRAFT SPECIFICATION — FROZEN FOR IMPLEMENTATION**  

---

## 1. Scope & Objective

This specification establishes the mathematical formula for computing cumulative chainwork across heterogeneous Proof-of-Work lanes (`SHA256D_ASIC` and `GENERAL_PURPOSE` Scrypt). 

The primary invariant: **Chain selection must strictly be determined by total validated cumulative chainwork, never by block count.** A chain containing many low-difficulty blocks must never win against a chain with higher cumulative energy commitment.

---

## 2. Mathematical Definition of Block Work

For any valid block $B$ with target $T_B = \text{bits\_to\_target}(B.\text{bits})$:

### 2.1 Raw Expected Iterations
The expected number of raw hash iterations required to find a solution is:
$$\text{raw\_work}(T_B) = \left\lfloor \frac{2^{256}}{T_B + 1} \right\rfloor$$

### 2.2 Thermodynamic Normalization & Lane Weights
Because different cryptographic algorithms demand fundamentally different CPU, memory, and energy resources per iteration, raw hash counts cannot be compared 1:1. 

A single Scrypt ($N=1024, r=1, p=1$) hash requires 2,048 internal SHA-256 operations and 128 KB of sequential memory access, taking approximately $\approx 2,000\times$ more energy than a single SHA-256D computation on standard microprocessors.

To reflect thermodynamic equivalence, the protocol defines **Lane Work Weights**:

$$\text{Weight}(\text{pow\_type}) = \begin{cases} 
1 & \text{for } \text{pow\_type} = 0 \text{ (SHA256D\_ASIC)} \\
2048 & \text{for } \text{pow\_type} = 1 \text{ (GENERAL\_PURPOSE Scrypt)}
\end{cases}$$

### 2.3 Weighted Block Work
The canonical chainwork contribution of block $B$ is:
$$\text{work}(B) = \text{raw\_work}(T_B) \times \text{Weight}(B.\text{pow\_type})$$

---

## 3. Cumulative Chainwork & Active Chain Tip Selection

### 3.1 Cumulative Chainwork Formula
For a chain of length $M$ starting at Genesis ($H=0$):
$$\text{Chainwork}(M) = \sum_{i=0}^{M} \text{work}(B_i)$$

### 3.2 Fork Choice Rule
Given two competing valid branches $\mathcal{C}_1$ and $\mathcal{C}_2$ sharing a common ancestor:
$$\text{Best Tip} = \begin{cases}
\mathcal{C}_1 & \text{if } \text{Chainwork}(\mathcal{C}_1) > \text{Chainwork}(\mathcal{C}_2) \\
\mathcal{C}_2 & \text{if } \text{Chainwork}(\mathcal{C}_2) > \text{Chainwork}(\mathcal{C}_1) \\
\text{Current Tip} & \text{if } \text{Chainwork}(\mathcal{C}_1) = \text{Chainwork}(\mathcal{C}_2) \text{ (First-Seen)}
\end{cases}$$

---

## 4. Formal Proof Against Low-Difficulty Grinding Attacks

### Scenario
An attacker attempts to reorganize the chain by mining thousands of rapid blocks on Lane B at maximum target (lowest difficulty `POW_LIMIT_TARGET` $T_{\max} = 0x00000fffff...$).

### Proof
Let $W_{\min} = \lfloor 2^{256} / (T_{\max} + 1) \rfloor \times 2048$.
Each block mined at minimum difficulty provides exactly $W_{\min}$ work.
If the honest network has an accumulated chainwork $\Delta W_{\text{honest}}$, the attacker must produce:
$$K \ge \frac{\Delta W_{\text{honest}}}{W_{\min}} \text{ blocks}$$
Under the independent LWMA-1 retargeting rule, as soon as the attacker mines blocks faster than the 120-second target interval, Lane B's target $T_B$ drops exponentially toward higher difficulty. Consequently:
1. The attacker cannot produce blocks indefinitely at $T_{\max}$.
2. The total work accumulated by the attacker remains strictly bounded by the actual computational power applied.
3. Block count $K$ confers zero advantage in fork selection; only $\sum \text{work}(B)$ decides the best tip.
$\blacksquare$
