# QuantyCoin Copilot & Agent Instruction Manual

## 1. Project Identity & Architecture
- **Project**: QuantyCoin 2.0 (`QTY2`), Protocol Version `70020`.
- **Core Architecture**: Independent SHA-256D Proof-of-Work Layer-1 cryptocurrency.
- **Authoritative Implementation**: The Python codebase (`core/`, `crypto/`, `network/`, `node/`, `wallet/`, `miner/`, `ui/`) is the verified operational stack.
- **Reference Codebase**: `src/` is an architectural reference / C++ experimental branch. Never import Bitcoin network identity, magic bytes, or genesis hashes into QuantyCoin.

## 2. Absolute Rules
1. **Never Invent Facts**: Never guess APIs, parameters, or test results. Always inspect directly before claiming or modifying.
2. **Consensus Invariance**: Never permit wallet, RPC, miner, or UI code to alter consensus rules defined in `core/consensus.py` or `core/genesis_constants.py`.
3. **Zero Secrets in Repository**: Never commit or log private keys, seeds, tokens, or external vault paths.
4. **Evidence-Gated Completion**: Any claimed fix or milestone must be backed by reproducible execution evidence in `docs/agent/EVIDENCE.md`.

## 3. Key Commands
- **Security Scanner**: `python scripts/verify_security.py`
- **Unit Tests**: `python tests/test_crypto.py`, `python tests/test_core.py`, `python tests/test_p2p.py`
- **Stratum Test**: `python tests/test_functional_stratum.py`
- **Full Test Runner**: `python tests/test_runner.py`
- **Stress & Chaos Matrix**: `python tests/test_multinode_stress.py`
