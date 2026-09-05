# QuantyCoin QTY4 Canonical Protocol Specification

**Protocol Version**: `70040` (`QTY4`)  
**Chain Identifier**: `quantycoin-4.0`  
**Status**: Authoritative Protocol Baseline  
**Date**: September 2026  

---

## 1. Protocol Architecture Summary

QuantyCoin QTY4 is an independent, post-quantum secure Layer-1 blockchain operating an Asymmetric Dual Proof-of-Work consensus engine with Weighted Cumulative Work fork choice:

1. **Dual-Lane Proof-of-Work**:
   - **Lane A (SHA-256D)**: Dedicated to industrial ASIC mining with a 120-second target interval and thermodynamic work weight $W_A = 1$.
   - **Lane B (RFC 7914 Scrypt 1024)**: Dedicated to consumer CPU/GPU mining with a 120-second target interval and thermodynamic work weight $W_B = 2048$.
   - **Combined Block Cadence**: 60 seconds nominal block time under dual-lane operation.
2. **Transaction Authorization**:
   - **NIST FIPS 204 ML-DSA-44**: Native post-quantum lattice digital signatures (`libqtydilithium`) with domain-separated sighash binding.
   - **Supported Modes**:
     - Mode 0 (`qty1q...`): Legacy Secp256k1 SegWit v0.
     - Mode 1 (`qty1p...`): Pure ML-DSA-44 Post-Quantum Witness v1.
     - Mode 2 (`qty1z...`): Dual-Authorization Hybrid Witness v2 (Secp256k1 + ML-DSA-44).
3. **Monetary Schedule**:
   - Total Maximum Supply: `21,000,000 QTY` (`2,100,000,000,000,000` satoshis).
   - Base Block Subsidy:
     - Lane A: `50 QTY` (`5,000,000,000` satoshis).
     - Lane B: `25 QTY` (`2,500,000,000` satoshis).
   - Halving Window: `2,100,000 blocks` (~4 years).
   - Coinbase Maturity: `100 blocks`.
4. **Network Parameters**:
   - Mainnet Magic: `0x51545934` (`QTY4`).
   - Mainnet Ports: P2P `19444`, RPC `19445`, Stratum V1 `3333`, Stratum V2 `3334`.

---

## 2. Inviolable Consensus Invariants

1. **Deterministic Execution**: All consensus arithmetic uses 64-bit integer values. Floating-point arithmetic is prohibited.
2. **Weighted Cumulative Work**: Fork-choice resolution evaluates cumulative energy-normalized chainwork rather than block count.
3. **Fail-Closed PQC**: Missing or unverified ML-DSA-44 native acceleration aborts validation immediately with zero fallback tolerance.
4. **Air-Gap Genesis**: Genesis block is generated and verified from 100% public inputs without private creator secrets.
