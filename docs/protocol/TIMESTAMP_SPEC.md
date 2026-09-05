# QuantyCoin QTY4 Timestamp Consensus Specification

**Protocol**: QTY4 (70040)  
**Consensus Properties**: Median-Time-Past (MTP) & Future Time Limit  

---

## 1. Median-Time-Past (MTP) Rule

To ensure strictly monotonic block progression and prevent timestamp manipulation:

### Definition
For a candidate block at height $H$:
1. Collect the timestamps of the previous $M = \min(11, H)$ active chain blocks:
   $$\mathcal{T} = \{\text{timestamp}(B_{H-1}), \text{timestamp}(B_{H-2}), \dots, \text{timestamp}(B_{H-M})\}$$
2. Sort $\mathcal{T}$ in ascending numerical order: $\mathcal{T}_{\text{sorted}} = [t_0, t_1, \dots, t_{M-1}]$.
3. The Median-Time-Past is:
   $$\text{MTP}(H) = t_{\lfloor M / 2 \rfloor}$$

### Consensus Invariant
$$\text{timestamp}(B_H) > \text{MTP}(H)$$
Any block with $\text{timestamp}(B_H) \le \text{MTP}(H)$ is consensus-invalid and rejected immediately.

---

## 2. Future Timestamp Limit

To prevent miners from forging timestamps arbitrarily far into the future:

$$\text{timestamp}(B_H) \le \text{AdjustedNetworkTime}() + 7200 \text{ seconds}$$

Where:
- $\text{AdjustedNetworkTime}()$ is the median of local node system time and connected peer time offsets.
- Allowed future drift is strictly limited to 2 hours (7200 seconds).
