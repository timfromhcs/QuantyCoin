# Security & Secret Isolation Instructions

## 1. Zero-Leak Policy
- **Local Secret Vault**: An air-gapped secret vault located outside the repository tree is canonical for private keys, raw nonce mining logs, and deployment secrets.
- **Never Commit Secrets**: Any file matching `*.secret`, `*.key`, `*.pem`, `*.seed`, `*.mnemonic` must be blocked by `.gitignore`.
- **Pre-Push Validation**: Always run `python scripts/verify_security.py` prior to commits and pushes.

## 2. Cryptographic Integrity
- PoW: Double-SHA256 only.
- Signing: RFC 6979 deterministic Secp256k1 ECDSA.
- Deserialization: Enforce byte bounds on all incoming P2P and RPC buffers.
