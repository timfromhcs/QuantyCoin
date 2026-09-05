# QuantyCoin 2.0 (QTY2) Open Questions & Trade-offs

This file tracks questions, architectural options under evaluation, and non-blocking backlogs.

---

## 1. Open Questions & Backlog

1. **Stratum V2 Extension**:
   - Priority: Post-v2.0 freeze.
   - Status: Stratum V1 is the primary production target. Architecture will provide clean interface hooks for V2 binary framing without compromising V1 reliability.

2. **P2P Compact Blocks**:
   - Priority: Post-IBD stabilization.
   - Status: BIP152-style compact blocks relay will be scaffolded behind feature flag, maintaining standard inv/getdata block relay as authoritative baseline.
