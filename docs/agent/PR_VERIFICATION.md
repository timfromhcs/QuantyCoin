# Pull Request Verification & Review Specification

**PR Title**: `QTY2: harden CI/CD, repository trust, branding and documentation`  
**Base Branch**: `main`  
**Head Branch**: `v2.0`  
**Merge Policy**: **NEVER_MERGE_MAIN (Review Only)**  

---

## 1. Pull Request Description

### Summary of Changes
This pull request delivers the comprehensive repository-quality, CI/CD, release packaging, branding, trust, and documentation hardening pass for **QuantyCoin QTY2 (Protocol 70020)**.

### Key Changes
1. **Legacy "v7" Eradication**:
   - Cleaned up obsolete version labels and headers across node daemon, RPC server coinbase tags, Qt6 desktop apps, Windows launchers, packaging scripts, and GitHub Actions workflows.
   - Standardized all binaries, installers, and archives on version `2.0.0` (QTY2).
2. **Error Masking Removal**:
   - Replaced all instances of `|| true` in build scripts (`packaging/linux/build_deb.sh`, `packaging/macos/build_dmg.sh`) and `.github/workflows/release.yml` with explicit environmental checks.
3. **Official Brand System**:
   - Created `/brand/` directory with 5 scalable SVGs (`logo.svg`, `logo-mark.svg`, `wordmark.svg`, `monochrome.svg`, `favicon.svg`).
   - Generated high-resolution social preview cards (`social-preview.png` 1200x630, `github-social-preview.png` 1280x640).
   - Authored formal design manual in `brand/brand-guidelines.md`.
4. **README Structure & Honesty Hardening**:
   - Strictly conformed to the 19 required sections.
   - Embedded vector logo in hero section.
   - Updated CI badge to canonical `ci.yml` and replaced static test badges with dynamic evidence-gated verification badges.
   - Added honest Nakamoto PoW throughput disclosures (14–28 TPS on standard transactions, 16 TX/s mempool ingestion benchmark).
5. **Machine-Readable Indexing**:
   - Synchronized `llms-full.txt` and verified `llms.txt` and `CITATION.cff`.

---

## 2. Evidence-Gated Verification Checklist

- [x] **Zero-Leak Security Audit**: `python scripts/verify_security.py` -> 0 leaks.
- [x] **Genesis Cryptographic Audit**: `python scripts/verify_genesis.py` -> 100% PASS.
- [x] **Documentation Integrity**: `python scripts/verify_documentation.py` -> 85/85 markdown links resolve.
- [x] **Unit & P2P Test Suite**: `python tests/test_crypto.py`, `python tests/test_core.py`, `python tests/test_p2p.py` -> PASS.
- [x] **Mining & Stratum Integration**: `python tests/test_functional_stratum.py` -> PASS.
- [x] **Multi-Node Hardness & Reorg**: `python tests/test_multinode_stress.py` -> PASS.
- [x] **Air-Gap Compliance**: No secrets, uncompressed keys, or vault paths in git tracking.
- [x] **Merge Policy**: Never auto-merge into `main`.

---

## 3. Reviewer Instructions

Maintainers can reproduce all verification checks locally:
```bash
# Verify security boundaries
python scripts/verify_security.py

# Verify genesis cryptographic integrity
python scripts/verify_genesis.py

# Verify documentation links
python scripts/verify_documentation.py

# Run functional test runner
python tests/test_runner.py
```
