# QuantyCoin Public Claim Ledger

**Audit Date**: 2026-09-05  
**Contract**: `QUANTYCOIN-REPO-REVAMP-2026` — Phase 02  
**Classification States**: `VERIFIED`, `IMPLEMENTED_BUT_NOT_FULLY_VERIFIED`, `EXPERIMENTAL`, `PLANNED`, `UNKNOWN`, `BLOCKED`  

---

## High-Impact Claims Inventory

| ID | Public Claim | Source Location | Evidence | Status | Confidence | Required Action | Replacement Text |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | "High-Performance Quantum & AI Era Layer-1 Blockchain" | `README.md:1`, `llms.txt:1` | None for "AI Era" or "Quantum" in Python core | `EXPERIMENTAL` | High | Reframe to focus on verified properties | "QuantyCoin 2.0 (QTY2): Independent SHA-256D Proof-of-Work Layer-1 Cryptocurrency" |
| **CLM-002** | "Delivering thousands of transactions per second on native Layer-1" | `README.md:97` | Mempool stress test: 16 TX/s; single-threaded validation: ~200-500 TX/s | `UNSUPPORTED` | High | Remove throughput exaggeration | "32 MB maximum block capacity with 60-second target block times, optimized for high transaction density" |
| **CLM-003** | "Release v7.0 / Protocol Version 70015" | `README.md:5`, `llms.txt:5` | Frozen in `core/genesis_constants.py` as Protocol 70020, Version 2.0.0 | `OUTDATED` | High | Correct version across all files | "QuantyCoin 2.0.0 (Protocol QTY2 / 70020)" |
| **CLM-004** | "Deterministic SHA-256D Proof-of-Work Consensus" | `core/block.py`, `core/consensus.py` | `tests/test_core.py`, `tests/test_functional_mining.py` (100% PASS) | `VERIFIED` | High | Retain as authoritative claim | "Authoritative double-SHA256 (SHA-256D) Proof-of-Work consensus" |
| **CLM-005** | "Air-Gapped Production Genesis Block" | `genesis/PUBLIC_GENESIS_MANIFEST.json` | `scripts/generate_and_verify_genesis.py`, runtime node assertion | `VERIFIED` | High | Retain with verifiable hash | "Independently verified Genesis block (`00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`)" |
| **CLM-006** | "LWMA-1 Difficulty Retargeting" | `core/consensus.py` | `tests/test_core.py`, `tests/test_functional_mining.py` | `VERIFIED` | High | Update window description from 144 to 45 blocks | "Linear-Weighted Moving Average (LWMA-1) retargeting every block over a 45-block window" |
| **CLM-007** | "Built-in Stratum V1/V2 Pool Server" | `README.md:84`, `README.md:100` | `miner/stratum.py` implements Stratum V1; V2 is not implemented | `IMPLEMENTED_BUT_NOT_FULLY_VERIFIED` | High | Remove V2 claim, verify V1 | "Native Stratum V1 mining pool server on TCP port 3333; Stratum V2 architecture extension point" |
| **CLM-008** | "Post-Quantum Cryptographic Security (Dilithium)" | `README.md:43`, `src/crypto/dilithium/` | Vendored in C++ `src/`; Python core currently uses Secp256k1 ECDSA | `EXPERIMENTAL` | High | Clearly separate Python baseline from C++ PQ research | "Secp256k1 ECDSA with Bech32 native witness addresses; C++ Dilithium integration under audit" |
| **CLM-009** | "10-Block Deep Reorganization Recovery" | `node/chainstate.py` | `tests/test_functional_reorg.py`, `tests/test_multinode_stress.py` | `VERIFIED` | High | Retain with test reproduction instructions | "Atomic UTXO rollback and cumulative PoW fork resolution verified up to 10+ block branch splits" |
| **CLM-010** | "Multi-Threaded JSON-RPC 2.0 Interface" | `node/rpc_server.py` | Functional across multi-node test suites on port 19889 | `VERIFIED` | High | Retain with API documentation | "Threaded JSON-RPC 2.0 server supporting standard node, wallet, and mining endpoints" |
| **CLM-011** | "Native Qt6 Desktop GUI Suite (4 Apps + Suite)" | `ui/` | Qt6 apps (`qt_node_app.py`, `qt_wallet_full_app.py`, `qt_miner_app.py`, etc.) | `IMPLEMENTED` | High | Document local Python run commands and packaging status | "Native Qt6 desktop applications for Node, Sovereign Wallet, Miner, and unified Suite" |
| **CLM-012** | "Precompiled Standalone Windows/Linux/macOS Release Installers Available" | `README.md:278-296` | Packaging scripts exist in `packaging/`; binary release assets must be built | `IMPLEMENTED_BUT_NOT_FULLY_VERIFIED` | High | Clarify source build vs precompiled installer availability | "Packaged via GitHub Actions and local scripts; source-build instructions documented" |
| **CLM-013** | "Instantaneous Settlement" | `README.md:43` | Block interval is 60s; transactions confirm on mined blocks | `UNSUPPORTED` | High | Remove claim; state actual confirmation time | "60-second target block time providing rapid on-chain transaction inclusion" |
| **CLM-014** | "Lightning Light Wallet Remote SPV RPC" | `ui/qt_lightning_wallet_app.py` | Connects via JSON-RPC to a node; not a full BIP37/157 SPV filter client | `IMPLEMENTED_BUT_NOT_FULLY_VERIFIED` | High | Clarify that light wallet connects via RPC client | "Lightweight wallet client connecting to local or remote QuantyCoin node RPC" |
| **CLM-015** | "50% Miner / 50% Treasury Fee Split" | `core/consensus.py` | Documented in `public_genesis.json`; block template coinbase division | `IMPLEMENTED` | High | Accurately document consensus fee allocation rules | "Protocol fee distribution model supporting community infrastructure and miners" |
