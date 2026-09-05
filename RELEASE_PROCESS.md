# QuantyCoin Official Release Process

**Protocol Version**: QTY2 (`70020`)  
**Standard**: Evidence-Gated Release Pipeline  

---

## 1. Release Gates & Prerequisites

A release may only be published if all the following gates pass:

1. **Security Gate**: `python scripts/verify_security.py` passes with zero leaks or credential patterns.
2. **Test Gate**: All unit and functional tests (`python tests/test_runner.py`) report 100% PASS with zero skipped or weakened assertions.
3. **Consensus Gate**: Genesis block parameters match `genesis/PUBLIC_GENESIS_MANIFEST.json` and node boots without runtime assertions.
4. **Git Hygiene**: Staged git status is completely clean with no untracked artifacts or temporary logs.

---

## 2. Release Packaging Pipeline

### Windows
- NSIS scripts in `packaging/windows/` generate:
  - `QuantyCoin-Node-Setup-v2.0.exe`
  - `QuantyCoin-Wallet-Setup-v2.0.exe`
  - `QuantyCoin-Miner-Setup-v2.0.exe`
  - `QuantyCoin-Suite-Setup-v2.0.exe`
- Portable Windows zip archive packaging.

### Linux
- `packaging/linux/build_deb.sh` generates `.deb` packages for Debian/Ubuntu.
- `packaging/linux/build_appimage.sh` generates standalone Linux AppImages.

---

## 3. Checksum Verification

Every released binary must have its SHA-256 checksum calculated and recorded in `SHA256SUMS.txt`:

```bash
sha256sum * > SHA256SUMS.txt
```

Users verify downloaded binaries via:
```bash
sha256sum -c SHA256SUMS.txt
```
