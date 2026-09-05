# QuantyCoin Independent Verification Center

This section contains step-by-step guides for independent reproduction and cryptographic verification.

---

## Documents

- [Independent Verification Guide](../../VERIFICATION.md): Complete instructions for running the test harness and verifying consensus parameters.
- [Build & Environment Reproducibility](../../REPRODUCIBILITY.md): Environment specifications, dependencies, and deterministic build instructions.
- [Evidence Ledger](../agent/EVIDENCE.md): Concrete cryptographic hashes, run logs, and execution evidence.
- [Failure Incident Protocol](../agent/FAILURES.md): Recorded failure incident reports, root cause analyses, and fixes.

---

## Quick Verification Checklist

1. **Zero-Leak Check**: `python scripts/verify_security.py` -> Reports `[PASS]`.
2. **Consensus Genesis Assertions**: Node boots with exact match to `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`.
3. **Core Unit Suite**: `python tests/test_core.py` -> Reports `100% PASS`.
4. **Stratum V1 Suite**: `python tests/test_functional_stratum.py` -> Reports `100% PASS`.
5. **Functional Multi-Node Suite**: `python tests/test_runner.py` -> Reports `100% PASS (0 failures)`.
6. **Stress & Reorg Matrix**: `python tests/test_multinode_stress.py` -> Reports `100% PASS`.
