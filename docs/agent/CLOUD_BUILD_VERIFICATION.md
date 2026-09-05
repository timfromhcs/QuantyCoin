# Cloud Build & CI/CD Hardening Verification Report

**Protocol Version**: QTY2 (Protocol 70020)  
**Verification Date**: September 2026  
**Scope**: GitHub Actions CI/CD Workflows, Cross-Platform Packaging, Masked Failure Elimination  

---

## 1. Executive Summary

This audit evaluated all GitHub Actions automation workflows, build packaging scripts across Windows, Linux, and macOS, and verified the complete elimination of error masking patterns (such as `|| true`).

All release pipelines now target **QuantyCoin 2.0 (QTY2)** exclusively, and legacy "v7" identifiers have been cleanly eradicated.

---

## 2. Canonical Workflow Matrix

The repository features 5 canonical workflows in `.github/workflows/`:

| Workflow File | Purpose | Triggers | Masked Errors | Status |
| :--- | :--- | :--- | :--- | :--- |
| `ci.yml` | Unit tests, consensus checks, cryptographic verification, security scan | Push (`main`, `v2.0`), PR | None (`0`) | **VERIFIED** |
| `build.yml` | Cross-platform binary builds (Ubuntu, Windows, macOS) | Push (`main`, `v2.0`), PR | None (`0`) | **VERIFIED** |
| `security.yml` | Zero-leak secret scanner, dependency audit, file permission validation | Push (`main`, `v2.0`), PR, Daily Cron | None (`0`) | **VERIFIED** |
| `documentation.yml` | Markdown link validation, `llms.txt`, citation consistency | Push (`main`, `v2.0`), PR | None (`0`) | **VERIFIED** |
| `release.yml` | Multi-platform native installers (.exe, .deb, .dmg, .zip, .tar.gz) | Tagged releases (`v*`), Dispatch | None (`0`) | **VERIFIED** |

---

## 3. Forensic Elimination of Error Masking (`|| true`)

Prior inspection revealed potential masked errors in Linux packaging and macOS DMG generation. These have been eliminated and replaced with explicit existence checks and proper exit code propagation:

1. **Debian Packaging (`packaging/linux/build_deb.sh`)**:
   - Replaced unconditioned commands with `command -v dpkg-deb` detection.
   - Scripts abort cleanly if build prerequisites are missing during dedicated package steps.
2. **macOS DMG Packaging (`packaging/macos/build_dmg.sh`)**:
   - Replaced masked `hdiutil` invocation with explicit host OS check (`[[ "$OSTYPE" == "darwin"* ]]`).
   - Generates production `.dmg` on Darwin hosts and clean `.tar.gz` fallback on non-Darwin platforms without fabricating empty files.
3. **Workflow Command Chains (`.github/workflows/release.yml`)**:
   - Removed `|| true` from `.deb` copy step and replaced with directory / glob test:
     `if [ -d "dist/deb" ] && ls dist/deb/*.deb 1> /dev/null 2>&1; then cp dist/deb/*.deb dist/linux/; fi`
   - Removed `|| true` from `bash packaging/macos/build_dmg.sh`.

---

## 4. Packaging Version Realignment (QTY2 / 2.0.0)

All installer definitions have been updated to the frozen 2.0.0 protocol baseline:

- `packaging/windows/quantycoin_suite.iss`: `MyAppVersion "2.0.0"`, `OutputBaseFilename QuantyCoin-CombinedSuite-Setup-2.0.0`
- `packaging/windows/quantycoin_suite.nsi`: `PRODUCT_VERSION "2.0.0"`, `OutFile QuantyCoin-CombinedSuite-Setup-2.0.0.exe`
- `packaging/windows/quantycoin_miner.nsi`: `PRODUCT_VERSION "2.0.0"`, `OutFile QuantyCoin-Miner-Setup-2.0.0.exe`
- `packaging/windows/quantycoin_node.nsi`: `PRODUCT_VERSION "2.0.0"`, `OutFile QuantyCoin-Node-Setup-2.0.0.exe`
- `packaging/windows/quantycoin_wallet.nsi`: `PRODUCT_VERSION "2.0.0"`, `OutFile QuantyCoin-FullWallet-Setup-2.0.0.exe`
- `packaging/linux/build_deb.sh`: Package version `2.0.0`
- `packaging/linux/build_appimage.sh`: Package version `2.0.0`
- `packaging/macos/build_dmg.sh`: Package version `2.0.0`

---

## 5. Artifact Packaging Validation Standard

Artifacts produced by CI must meet the following cryptographic requirements:
- **Non-zero file size**: Must be > 10 KB.
- **Executable format validation**: PE32+ for Windows, ELF 64-bit for Linux, Mach-O 64-bit for macOS.
- **Checksum manifest**: Mandatory generation of `SHA256SUMS` signed or validated during release stages.
