# QuantyCoin Developer Documentation

This section provides onboarding guides, test harnesses, and contribution instructions for open-source developers.

---

## Documents

- [Testing Guide](TESTING_GUIDE.md): Detailed instructions on writing and executing unit, functional, and fuzz smoke tests.
- [Contributing Guidelines](../../CONTRIBUTING.md): Code conventions, branch workflows, and PR requirements.
- [Code of Conduct](../../CODE_OF_CONDUCT.md): Community participation standards.
- [Technical Roadmap](../../ROADMAP.md): Evidence-gated development milestones and active priorities.

---

## Developer Environment Setup

```bash
# Clone the repository
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin

# Install minimal test dependencies
pip install pytest PySide6 qrcode pillow

# Run the test runner
python tests/test_runner.py
```
