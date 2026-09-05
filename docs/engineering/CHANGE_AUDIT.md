# QuantyCoin QTY4 Protocol Rebuild Change Audit

**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Target Branch**: `main`  
**Working Branch**: `feature/qty4-consensus-rebuild`  
**Date**: 2026-09-05  

---

## 1. Overview of Changes

The QTY4 rebuild was executed to eliminate technical debt, eliminate floating-point arithmetic from the consensus engine, establish a completely new cryptographic chain identity, regenerate the public genesis block under 100% fair launch terms, and implement rigorous consensus vector and adversarial testing.

---

## 2. File-by-File Change Audit

### A. Consensus Core (`core/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `core/genesis_constants.py` | **Modified** | Updated to QTY4 constants: Protocol `70040`, Magic `0x51545934`, ports 19444/19445/3333/3334, new Genesis hash `000004eb...`, public payout address `qty1qu9zt...`. |
| `core/money.py` | **Added** | Implemented `Amount` class enforcing pure 64-bit integer arithmetic, bounds `[0, MAX_MONEY_SATOSHIS]`, and zero floating-point operations. |
| `core/consensus.py` | **Modified** | Replaced float subsidy calculation with bitwise right-shift; added strict compact target decoder; thermodynamic chainwork calculation ($W_A=1, W_B=2048$); integer LWMA-1 difficulty adjustment. |
| `core/validation.py` | **Added** | Implemented 12-stage consensus validation pipeline (`CheckBlock`, `CheckPoW`, `CheckCoinbase`, `CheckMoney`, `CheckWitnessAndScripts`). |
| `core/transaction.py` | **Modified** | Enforced integer `MAX_MONEY_SATOSHIS` in `TxOut`; updated PQC sighash domain tag to `b"QUANTYCOIN_QTY4_PQC_SIGHASH_V1"`; added structural validation. |
| `core/block.py` | **Modified** | Added structural verification for blocks and transactions; strict compact target bounds validation in `verify_pow()`. |

### B. Node & State Machine (`node/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `node/chainstate.py` | **Modified** | Bootstraps cleanly against QTY4 genesis hash `000004eb...`; runtime consensus assertion check. |
| `node/rpc_server.py` | **Modified** | Updated default ports to 19445; added dual-PoW, chainwork, and PQC migration RPC endpoints. |
| `node/daemon.py` | **Modified** | Updated network magic `0x51545934` and port configuration for QTY4. |

### C. Networking & Mining (`network/`, `miner/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `network/protocol.py` | **Modified** | Default magic updated to `0x51545934` (`QTY4`); 24-byte wire framing assertions. |
| `miner/engine.py` | **Modified** | Support for dual-lane SHA-256D and Scrypt mining threads targeting QTY4 header structures. |
| `miner/stratum_v2.py`| **Modified** | Port 3334 binary framing engine with dual-lane multiplexing. |

### D. Genesis Block & Verification (`genesis/`, `scripts/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `genesis/public/` | **Added** | Public genesis manifest, raw header hex, Merkle root, parameter JSON, and documentation. |
| `scripts/verify_genesis.py` | **Rewritten** | Authoritative 6-gate QTY4 consensus and dual-path verification engine; eliminated obsolete QTY2 logic. |
| `scripts/verify_documentation_consistency.py` | **Added** | Machine audit ensuring 100% parameter synchronization across all 23 active documents, manifests, and specs. |
| `scripts/mine_qty4_genesis.py` | **Added** | Deterministic genesis block miner from 100% public inputs. |
| `scripts/verify_qty4_genesis_dual_path.py` | **Added** | Dual-path independent cross-validator ensuring byte-for-byte reproducibility between Core and standalone standard library. |
| `scripts/generate_qty4_vectors.py` | **Added** | Generates 25 verified JSON test vectors across 6 consensus categories. |
| `scripts/verify_security.py` | **Modified** | Pre-commit/CI secret scanner inspecting against external vault references. |
| `scripts/generate_and_verify_genesis.py` | **Deleted** | Removed obsolete single-lane QTY2 generator. |
| `scripts/mine_genesis_vault.py` | **Deleted** | Removed obsolete non-canonical QTY2 generator. |
| `public_genesis.json` | **Updated** | Synchronized to canonical QTY4 manifest matching `genesis/PUBLIC_GENESIS_MANIFEST.json`. |
| `.github/workflows/*.yml` | **Modified** | Updated all CI workflows (`security.yml`, `ci.yml`, `documentation.yml`, `build.yml`, `release.yml`) for QTY4 gate enforcement. |

### E. Specification & Architecture (`spec/`, `docs/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `spec/qty4/*.json` | **Added** | Machine-readable specifications for consensus, PoW, PQC, network, transaction, and genesis. |
| `docs/protocol/*.md` | **Added** | 11 comprehensive protocol specifications: `QTY4_SPEC.md`, `CONSENSUS_RULES.md`, `POW_SPEC.md`, `DIFFICULTY_SPEC.md`, `CHAINWORK_SPEC.md`, `TIMESTAMP_SPEC.md`, `PQC_SPEC.md`, `ADDRESS_SPEC.md`, `SERIALIZATION_SPEC.md`, `NETWORK_SPEC.md`, `GENESIS_SPEC.md`. |
| `docs/STATUS.md` | **Added** | Subsystem readiness and protocol status. |
| `docs/CONSENSUS_ASSURANCE.md` | **Added** | Formal proofs of zero-float arithmetic, compact target bounds, and chainwork thermodynamics. |
| `docs/BUILD_MATRIX.md` | **Added** | Platform, compiler, and Python version compatibility matrix. |
| `docs/SECURITY_ASSURANCE.md` | **Added** | Proofs of air-gapped secret isolation and hostile input mitigations. |
| `docs/GENESIS_REPRODUCTION.md` | **Added** | Standalone guide and script for independent genesis reproduction. |
| `docs/engineering/REPOSITORY_FORENSIC_AUDIT.md` | **Added** | Forensic codebase audit and legacy subsystem assessment. |
| `docs/engineering/VERIFICATION_MATRIX.md` | **Added** | Test execution results and pass criteria matrix. |
| `docs/engineering/CHANGE_AUDIT.md` | **Added** | Complete change tracking and rationale documentation. |

### F. Adversarial & Functional Testing (`tests/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `tests/test_adversarial_qty4.py` | **Added** | 10 hostile input attack vectors (target overflow, fuzz headers, PQC bitflip, hybrid bypass, UTXO non-mutation). |
| `tests/test_dualpow_security_simulation.py` | **Added** | Lane disappearance simulation, anti-grinding chainwork test, and hashrate benchmark. |
| `tests/vectors/qty4/*` | **Added** | 25 JSON consensus test vector files. |

### G. Brand Identity & Visual Assets (`brand/`)
| File | Change Type | Rationale & Summary |
| :--- | :---: | :--- |
| `brand/logo.svg` | **Modified** | High-contrast vector logo. |
| `brand/logo-dark.svg`, `brand/logo-light.svg` | **Added** | Dark/light theme vector logos with AAA contrast ratio. |
| `brand/icon.svg` | **Added** | Minimalist square icon. |
| `brand/colors.json`, `brand/BRAND_GUIDE.md` | **Added** | Formal color palette and accessibility guidelines. |
