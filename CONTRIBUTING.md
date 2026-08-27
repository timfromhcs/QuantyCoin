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
   Before submitting a PR, ensure all test suites pass with 100% success:
   ```bash
   python tests/test_crypto.py
   python tests/test_core.py
   python tests/test_p2p.py
   python tests/test_multinode_stress.py
   ```
5. **Submitting Pull Requests**:
   - Write clear, conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
   - Open a Pull Request against the `main` branch.
   - Describe the motivation, changes made, and test results.
