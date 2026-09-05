# QuantyCoin Protocol Security Gates & Audit Criteria

**Document**: docs/agent/SECURITY_GATES.md  
**Protocol Version**: QTY2 (70020)  
**Security Standard**: NIST FIPS 204 ML-DSA Transaction Authorization & Dual-PoW Consensus  

---

## 1. Mandatory Pre-Release Security Gates

| Gate ID | Subsystem | Validation Requirement | Verification Command | Gate Status |
| :--- | :--- | :--- | :--- | :--- |
| **GATE-PQC-01** | Post-Quantum Cryptography | Zero pseudo-crypto fallbacks. Native C library (libqtydilithium) mandatory. Fail closed if missing. | python -m unittest tests/test_pqc_dualpow_sv2.py | **PASSED** |
| **GATE-PQC-02** | Signature Non-Malleability | Single-bit alterations or corrupted public keys strictly rejected. | 	est_07_reject_pseudo_crypto_and_malleated_signatures | **PASSED** |
| **GATE-PQC-03** | Cross-Mode Replay Prevention | Classical ECDSA signatures rejected on ML-DSA witness programs. | 	est_08_cross_mode_replay_attack_prevention | **PASSED** |
| **GATE-POW-01** | Thermodynamic Chainwork | Fork choice strictly determined by cumulative energy ($\sum W_i \cdot \lfloor 2^{256}/(T+1) floor$). | 	est_09_thermodynamic_chainwork_defeats_low_difficulty_spam | **PASSED** |
| **GATE-POW-02** | Failover Liveness | Network sustains uninterrupted block production if Lane A or Lane B ceases. | 	est_02_dual_pow_mining_and_verification | **PASSED** |
| **GATE-UTXO-01** | Legacy UTXO Audit & Migration | Wallets identify vulnerable classical outputs and build automated sweep transactions. | 	est_06_hd_wallet_pqc_integration | **PASSED** |
| **GATE-SV2-01** | Stratum V2 Protocol | 6-byte binary framing, dual-lane channel multiplexing, and low-latency job distribution. | 	est_04_stratum_v2_binary_protocol | **PASSED** |
| **GATE-LEAK-01** | Anti-Leak Vault Security | Repository scanning detects zero private keys, seeds, nonces, or vault artifacts. | python scripts/verify_security.py | **PASSED** |
| **GATE-DOCS-01** | Documentation Integrity | 100% link resolution across all documentation trees. Zero broken cross-references. | python scripts/verify_documentation.py | **PASSED** |

---

## 2. Threat Vector Mitigations

1. **Quantum Private Key Extraction (Shor's Algorithm)**:
   - *Mitigation*: Pure ML-DSA (qty1p...) and Hybrid (qty1z...) witness programs utilize Module-Lattice-Based Digital Signature Standard (FIPS 204). Secp256k1 public keys are never exposed on-chain until spent, and post-quantum programs protect the primary spend authorization.
2. **Rented-GPU 51% Attack on Lane B**:
   - *Mitigation*: Lane B thermodynamic weight is normalized ( = 2048$). Mined blocks at high targets accumulate proportionally low chainwork. Cumulative thermodynamic work prevents low-cost chain reorganizations.
3. **Mempool Sniping of Classical ECDSA Transactions**:
   - *Mitigation*: Phased migration strategy (MIGRATION_SPEC.md). Node RPC getaddressinfo actively flags vulnerable classical addresses and recommends migration sweeps.\n