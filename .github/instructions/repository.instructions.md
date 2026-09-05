# Repository Engineering Instructions

## 1. Directory Structure & Boundaries
- `core/`: Consensus, block validation, transactions, UTXO set, mempool. Must remain deterministic, endian-explicit, and platform-independent.
- `crypto/`: Mathematical primitives. Never invent custom algorithms.
- `network/`: Wire framing and peer handling. Treat all network input as untrusted and potentially hostile.
- `node/`: Chainstate and JSON-RPC 2.0 server.
- `miner/`: SHA-256D engine and Stratum V1 server.
- `wallet/`: BIP39/44 key derivation and transaction signing.
- `ui/`: Native Qt6 applications.
- `tests/`: Automated unit, functional, and stress test suites.
- `docs/`: Technical documentation architecture.

## 2. Commit & Code Hygiene
- Use conventional commit messages: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`.
- Work on dedicated feature/milestone branches.
- Run `python scripts/verify_security.py` prior to staging changes.
