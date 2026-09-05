# QuantyCoin Independent Verification Center

This section contains step-by-step guides for independent reproduction and cryptographic verification.

---

## Documents

- [Independent Verification Guide](../../VERIFICATION.md): Complete instructions for running the test harness and verifying consensus parameters.
- [Genesis Reproduction Guide](../GENESIS_REPRODUCTION.md): Step-by-step public genesis block reproduction and standalone verifier.
- [Consensus Assurance](../CONSENSUS_ASSURANCE.md): Mathematical invariants, zero-float proof, and chainwork weighting.
- [Security Assurance](../SECURITY_ASSURANCE.md): Vault isolation proofs and hostile input defenses.
- [Build & Environment Reproducibility](../../REPRODUCIBILITY.md): Environment specifications, dependencies, and deterministic build instructions.

---

## Quick Verification Checklist

1. **Zero-Leak Check**: `python scripts/verify_security.py` -> Reports `[PASS]`.
2. **Canonical Genesis Audit**: `python scripts/verify_genesis.py` -> Reports `[PASS]`.
3. **Dual-Path Genesis Reproduction**: `python scripts/verify_qty4_genesis_dual_path.py` -> Reports `[SUCCESS] 100% Byte-for-Byte Match`.
4. **Core Unit Suite**: `python tests/test_core.py` -> Reports `100% PASS`.
5. **Stratum V1 Suite**: `python tests/test_functional_stratum.py` -> Reports `100% PASS`.
6. **Adversarial Hardening**: `python tests/test_adversarial_qty4.py` -> Reports `100% PASS (10/10)`.
7. **Dual-PoW Security Simulation**: `python tests/test_dualpow_security_simulation.py` -> Reports `100% PASS (3/3)`.
8. **Functional Multi-Node Suite**: `python tests/test_runner.py` -> Reports `100% PASS (0 failures)`.
9. **Stress & Reorg Matrix**: `python tests/test_multinode_stress.py` -> Reports `100% PASS`.
