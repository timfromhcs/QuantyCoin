# QuantyCoin Platform & Build Matrix

**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Target Environments**: Windows & Linux (x86_64, aarch64)  

---

## 1. Supported Platform Matrix

| Platform | Architecture | Status | Python Versions | Core Engine | Native GUI (Qt6) |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **Windows 10 / 11 / Server** | `x86_64` | **Tier 1 (Full Support)** | 3.10, 3.11, 3.12, 3.13 | :white_check_mark: Supported | :white_check_mark: Supported |
| **Ubuntu 20.04 / 22.04 / 24.04** | `x86_64`, `aarch64` | **Tier 1 (Full Support)** | 3.10, 3.11, 3.12, 3.13 | :white_check_mark: Supported | :white_check_mark: Supported |
| **Debian 11 / 12** | `x86_64`, `aarch64` | **Tier 1 (Full Support)** | 3.10, 3.11, 3.12, 3.13 | :white_check_mark: Supported | :white_check_mark: Supported |
| **Fedora / RHEL / CentOS** | `x86_64`, `aarch64` | **Tier 1 (Full Support)** | 3.10, 3.11, 3.12, 3.13 | :white_check_mark: Supported | :white_check_mark: Supported |
| **Arch Linux / Manjaro** | `x86_64` | **Tier 1 (Full Support)** | 3.10, 3.11, 3.12, 3.13 | :white_check_mark: Supported | :white_check_mark: Supported |

---

## 2. Dependency Matrix

### Core Protocol Engine (Zero External Dependencies)
The core node daemon, consensus validation pipeline, cryptographic engine, and P2P wire stack run exclusively on the Python standard library:
- `hashlib`, `hmac`, `secrets`, `os`, `sys`
- `socket`, `select`, `struct`, `threading`, `time`
- `sqlite3`, `json`, `pathlib`, `typing`

### Optional Desktop Application Suite (PySide6)
- `PySide6` (Qt 6.5+)
- `pillow` (image rendering and icon scaling)
- `qrcode` (payment address QR generation)

### Test Harness & Developer Tooling
- `pytest` (unit & functional test runner)

---

## 3. Installation & Build Instructions

### Minimal Node & CLI Setup (All Platforms)
```bash
# Clone the repository
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin

# Verify clean environment
python scripts/verify_security.py

# Run the consensus test runner
python tests/test_runner.py
```

### Full Desktop GUI Setup
```bash
# Install UI dependencies
pip install -r packaging/requirements.txt
# Alternatively:
pip install PySide6 pillow qrcode pytest

# Launch the unified QuantyCoin Master Suite
python ui/qt_suite_app.py
```

---

## 4. Native Release Packaging

### Windows (NSIS Installer & Portable Zip)
Packaging scripts are located in `packaging/windows/`:
- `QuantyCoin-Node-Setup-4.0.0.exe`: Standalone Full Node Manager
- `QuantyCoin-Wallet-Setup-4.0.0.exe`: Sovereign Post-Quantum Wallet
- `QuantyCoin-Miner-Setup-4.0.0.exe`: Dual-PoW Mining Suite
- `QuantyCoin-Suite-Setup-4.0.0.exe`: Unified 4-in-1 Control Center

### Linux (Debian Package & AppImage)
- Debian `.deb` builder: `packaging/linux/build_deb.sh`
- AppImage builder: `packaging/linux/build_appimage.sh`
- Systemd service definition: `packaging/linux/quantyd.service`

---

## 5. Continuous Integration Matrix

Every pull request and release build executes across:
1. `windows-latest` (MSVC build environment, Python 3.11 & 3.12)
2. `ubuntu-latest` (GCC 12 build environment, Python 3.10, 3.11, 3.12)
3. Automated security scanner (`scripts/verify_security.py`)
4. Link and documentation validator (`scripts/verify_documentation.py`)
5. Dual-path genesis validator (`scripts/verify_qty4_genesis_dual_path.py`)
