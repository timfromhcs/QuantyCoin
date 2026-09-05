# QuantyCoin 2.0 (QTY2) Repository Hardening Baseline

**Document ID**: `QTY2-HARDENING-BASELINE-2026`  
**Contract ID**: `QUANTYCOIN-QTY2-REPO-HARDENING-2026`  
**Mode**: Autonomous Long-Horizon Engineering  
**Completion Policy**: Evidence-Gated  
**Merge Policy**: `FORBIDDEN` (`NEVER_MERGE_MAIN`)  
**Date**: 2026-09-05  

---

## 1. Baseline Git Forensics & Verification

| Forensic Item | Target Value | Actual Inspected Value | Status |
| :--- | :--- | :--- | :--- |
| **Current Branch** | `v2.0` | `v2.0` | **CONFIRMED** |
| **Claimed Head Commit** | `c61990d` | `c05ddde` (fast-forwarded following merge of PR #2 commit `d208415`) | **CONFIRMED** |
| **Remote Origin** | `https://github.com/timfromhcs/QuantyCoin.git` | `https://github.com/timfromhcs/QuantyCoin.git` | **CONFIRMED** |
| **Working Tree** | Clean | Clean (0 untracked, 0 modified) | **CONFIRMED** |
| **Base Branch** | `main` | `main` | **CONFIRMED** |
| **Relationship to Main**| Aligned | `v2.0` aligned with `origin/main` at `c05ddde` | **CONFIRMED** |

---

## 2. Forensic Workflow & CI/CD Inspection (Phase 02 Baseline)

The repository workflow suite has been audited for legacy, duplicate, or unsafe patterns:

| Workflow File | Purpose | Detected Anti-Patterns | Action Needed |
| :--- | :--- | :--- | :--- |
| `.github/workflows/ci.yml` | Multi-OS test runner | None (`|| true` not present, fails fast) | Retain as canonical test matrix |
| `.github/workflows/security.yml`| Secret & Genesis scan | None (strict zero-leak, deterministic) | Retain as canonical security gate |
| `.github/workflows/documentation.yml`| Link & AST validation | None (84 links verified) | Retain as canonical doc gate |
| `.github/workflows/build.yml` | Cloud build verification | Smoke build checks CLI binaries | Verify smoke build steps, no placeholder binaries |
| `.github/workflows/release.yml`| Native distribution builder | Legacy v7 references in comments | Clean up legacy v7 references and ensure QTY2 release naming only |
| `.github/workflows/build-and-address-tests.yml`| Legacy Knots build | Missing minisketch test | Already deleted in commit `47ed324` |
| `.github/workflows/qty2_ci.yml`| Redundant test runner | Duplicate of `ci.yml` | Already consolidated in commit `47ed324` |
| `.github/workflows/release_v7.yml`| Legacy release name | Stale v7 release naming | Already consolidated in commit `47ed324` |

---

## 3. Subsystem Health & Baseline Inventory

1. **Source Tree**:
   - `core/`, `crypto/`, `network/`, `node/`, `wallet/`, `miner/`, `ui/`: Active, operational Python Layer-1 node.
   - `src/`: Upstream Bitcoin Knots C++ reference fork containing experimental post-quantum research patches.
2. **Consensus Engine**:
   - Algorithm: Nakamoto SHA-256D Proof-of-Work.
   - Target Block Interval: 60 seconds.
   - Difficulty Adjustment: LWMA-1 (window: 45 blocks).
   - Subsidy: 50 QTY initially, halving every 2,100,000 blocks, 21,000,000 QTY cap.
   - Genesis Block Hash: `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`.
3. **Security Boundary**:
   - Strict zero-leak enforcement via `scripts/verify_security.py`.
   - Complete isolation of private keys and raw nonces in local air-gapped secret vault.
4. **Documentation Architecture**:
   - Root: Entrypoints (`README.md`, `TRUST.md`, `SECURITY.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`).
   - `docs/`: 8 structured categories (`architecture/`, `protocol/`, `security/`, `verification/`, `operations/`, `development/`, `repository/`, `archive/`).
