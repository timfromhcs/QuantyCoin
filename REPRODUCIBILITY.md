# QuantyCoin Build & Environment Reproducibility

**Goal**: Ensure that any build or execution of QuantyCoin produces deterministic cryptographic outputs and identical behavior across platforms.  
**Protocol Version**: QTY4 (`70040`)  

---

## 1. Supported Environments

| Operating System | Architecture | Supported Python Versions | Compiler (C++ Tree) |
| :--- | :--- | :--- | :--- |
| **Ubuntu / Debian Linux** | x86_64, aarch64 | Python 3.10, 3.11, 3.12, 3.13 | GCC 11+, Clang 14+ |
| **Windows** | x86_64 | Python 3.10, 3.11, 3.12, 3.13 | MSVC 2022 / MinGW-w64 |

---

## 2. Deterministic Dependencies

The core protocol stack avoids external C-extensions for maximum cross-platform reproducibility:
- Standard Python Library: `hashlib`, `socket`, `struct`, `sqlite3`, `threading`, `json`, `os`, `sys`, `time`
- Optional Desktop GUI: `PySide6` (Qt6), `pillow`, `qrcode`
- Build / Test: `pytest`

To install the minimal development environment:
```bash
pip install -r packaging/requirements.txt 2>/dev/null || pip install PySide6 pytest pillow qrcode
```

---

## 3. Cryptographic Determinism Checks

- **Pure Integer Monetary State**: Checked 64-bit integer class (`core.money.Amount`) eliminating floating-point rounding divergence across CPU architectures.
- **ECDSA Signatures**: Deterministic RFC 6979 nonce generation ensures identical signatures for identical private key and message digest pairs.
- **ML-DSA-44 Signatures**: Native NIST FIPS 204 C lattice acceleration (`libqtydilithium`) with deterministic verification.
- **Transaction Hash (TxID)**: Double-SHA256 over canonical byte serialization.
- **Merkle Root**: Binary tree double-SHA256 with duplicate-odd balancing matching standard Bitcoin Core convention.
- **Genesis Block**: Bit-for-bit identical serialization (246 bytes) and hash across all operating systems (`scripts/verify_qty4_genesis_dual_path.py`).
