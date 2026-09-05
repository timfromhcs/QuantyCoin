# QuantyCoin 2.0 (QTY2) Failure Incident Protocol & Log

When an error, test failure, regression, or leak is encountered, it must be documented here with reproduction steps, root cause analysis, regression test, and fix confirmation.

---

## Incidents Log

### Incident INC-001: Genesis Payout Address Hardcoded in Tests & RPC Fallbacks
- **Observed**: `MiningTest` failed on `assert bal["balance"] == 300.0`. Balance was 250.0 instead of 300.0.
- **Root Cause**: `tests/test_functional_mining.py`, `tests/test_framework.py`, `node/rpc_server.py`, and UI apps hardcoded the old pre-v2 genesis payout address string instead of importing `GENESIS_COINBASE_PAYOUT_ADDRESS` dynamically from `core.genesis_constants`.
- **Fix**: Update all occurrences to import and reference `GENESIS_COINBASE_PAYOUT_ADDRESS` from `core.genesis_constants`.
- **Regression Test**: Rerun `tests/test_functional_mining.py` and full test suite.

### Incident INC-002: Hardcoded Genesis Timestamp in Multi-Node Stress Test
- **Observed**: `test_multinode_stress.py` failed on `Block 1 failed: Block timestamp too far in past`.
- **Root Cause**: `tests/test_multinode_stress.py` used the deprecated hardcoded pre-v2 genesis timestamp `1771804800` instead of importing `GENESIS_TIMESTAMP` (`1788600000`).
- **Fix**: Replaced hardcoded values with `GENESIS_TIMESTAMP` imported from `core.genesis_constants`.
- **Regression Test**: Rerun `tests/test_multinode_stress.py`. All 4 tests passed 100%.
### Incident INC-003: Stale v7 Artifact Names & Masked Failures in Cloud Packaging
- **Observed**: Packaging scripts and `.github/workflows/release.yml` retained `v7.0` naming and utilized `|| true` to swallow missing platform tools (`dpkg-deb`, `hdiutil`).
- **Root Cause**: Incremental development across prior iterations had left hardcoded legacy version labels and defensive suppression constructs in packaging scripts.
- **Fix**: Updated all InnoSetup (.iss), NSIS (.nsi), Debian, and macOS packaging scripts to protocol version `2.0.0` and replaced `|| true` with conditional tool existence checks.
- **Regression Test**: Run `scripts/verify_documentation.py`, `scripts/verify_security.py`, and inspect release workflow syntax.

### Incident INC-004: Insecure Pseudo-Crypto Fallback in PQC Subsystem
- **Observed**: Code audit discovered `_fallback_verify`, `_fallback_sign`, and `_fallback_keypair_from_seed` in `crypto/mldsa.py` that accepted invalid signatures as valid if byte length matched.
- **Root Cause**: A temporary mock fallback engine using SHAKE-256 had been introduced for portability when native C library compilation was absent.
- **Fix**: Completely excised all `_fallback_*` methods from `crypto/mldsa.py`. Mandated genuine native NIST FIPS 204 acceleration (`libqtydilithium`) and introduced `CryptographicBackendUnavailableError` to fail closed if the native engine cannot be loaded.
- **Regression Test**: Executed `test_07_reject_pseudo_crypto_and_malleated_signatures` in `tests/test_pqc_dualpow_sv2.py` verifying synthetic and length-padded signatures are strictly rejected.


