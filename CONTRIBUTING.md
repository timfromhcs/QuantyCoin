# Contributing to QuantyCoin (QTY)

We welcome contributions from developers, cryptographic researchers, and open-source blockchain engineers!

## Getting Started

1. **Fork the Repository**: Click "Fork" on GitHub and clone your fork locally.
2. **Branch Naming**: Use descriptive branch names:
   - `feature/your-feature-name`
   - `fix/issue-description`
   - `docs/improvement-area`
3. **Environment Setup**:
   ```bash
   git clone https://github.com/<your-username>/QuantyCoin.git
   cd QuantyCoin
   pip install qrcode pyinstaller
   ```
4. **Code Quality & Testing**:
   Before submitting a PR, ensure all verification and test suites pass with 100% success:
   ```bash
   # Zero-leak security scan
   python scripts/verify_security.py

   # Documentation and link integrity
   python scripts/verify_documentation.py

   # Genesis consensus validation
   python scripts/verify_genesis.py

   # Core cryptographic and protocol unit tests
   python tests/test_crypto.py
   python tests/test_core.py
   python tests/test_p2p.py
   python tests/test_functional_stratum.py

   # Full multi-node integration test runner
   python tests/test_runner.py

   # Multi-node stress, hardness & reorg matrix
   python tests/test_multinode_stress.py
   ```

5. **Submitting Pull Requests**:
   - Write clear, conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
   - Open a Pull Request against the `main` branch.
   - Describe the motivation, changes made, and test results.
   - Adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) and [Support Guide](SUPPORT.md).
