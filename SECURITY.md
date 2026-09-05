# QuantyCoin Security Policy

**Last Updated**: 2026-09-05  
**Protocol Version**: QTY3 (`70020`)  

---

## 1. Supported Versions

| Version | Protocol Version | Support Status | Notes |
| :--- | :--- | :--- | :--- |
| **3.0.x (QTY3)** | **70020** | :white_check_mark: **Supported (Current Production Baseline)** | Dual-PoW, ML-DSA-44 PQC, Stratum V2, active maintenance. |
| **2.0.x (QTY2)** | **70020** | :white_check_mark: Supported (Consensus-Compatible Baseline) | Previous consensus iteration; upgrade recommended. |
| < 2.0.0 | < 70020 | :x: Unsupported (Deprecated Genesis) | Pre-rebuild legacy iterations. Nodes should upgrade. |

---

## 2. Reporting Security Vulnerabilities

The QuantyCoin core development team treats consensus safety, cryptographic correctness, and node stability with the highest priority.

If you identify a vulnerability (e.g. consensus fork risk, cryptographic verification flaw, RPC remote code execution, P2P memory exhaustion, or secret leakage):

1. **DO NOT** create a public issue, discussion, or pull request on GitHub.
2. Send an encrypted or plain email with detailed technical steps and proof-of-concept to:  
   **`timfromhcs@gmail.com`**
3. **Response SLA**:
   - **Initial Acknowledgement**: Within 24 hours.
   - **Triage & Severity Rating**: Within 48 hours.
   - **Patch Timeline**: Coordinated release within 7 days for critical vulnerabilities.
4. **Coordinated Disclosure**: Disclosures will be credited in release notes and security advisories after patches have been published.

---

## 3. Zero-Leak Secret Boundary

The repository enforces strict air-gapped isolation:
- All Genesis generation material, private keys, seeds, and mnemonics remain in an external air-gapped secret vault.
- Automated pre-push and pre-commit checks ([`scripts/verify_security.py`](scripts/verify_security.py)) block any commit containing secret key patterns or private file extensions.

---

## 4. Threat Model & Security Boundaries

A formal analysis of network attack vectors, hostile input sanitization, RPC authentication, and UTXO integrity is available in [THREAT_MODEL.md](THREAT_MODEL.md).
