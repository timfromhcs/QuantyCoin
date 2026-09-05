# QuantyCoin Protocol Rebuild State: QTY4 Consensus Rebuild

**Branch**: `feature/qty4-consensus-rebuild`  
**Current Phase**: QTY4 Complete Consensus Rebuild & Formal Verification  
**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Genesis Hash**: `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`  
**Last Updated**: 2026-09-05  

---

## Subsystem Status Matrix

| Subsystem | Status | Notes |
| :--- | :--- | :--- |
| **Agent State & Policy** | **VERIFIED** | `AGENTS.md` active, `docs/agent/` state files continuously maintained. |
| **Local Secret Vault** | **VERIFIED** | Local air-gapped secret vault structure operational outside git (`QuantySecrets/`). |
| **Zero-Leak Git Policy** | **VERIFIED** | Enforced by `.gitignore` and verified by `scripts/verify_security.py` (0 secrets). |
| **Monetary Calculation** | **VERIFIED** | Pure 64-bit integer arithmetic via `core.money.Amount`. Zero float tolerance. |
| **Consensus Freeze & Specs** | **VERIFIED** | Specs: `QTY4_SPEC.md`, `CONSENSUS_RULES.md`, `POW_SPEC.md`, `DIFFICULTY_SPEC.md`, `CHAINWORK_SPEC.md`, `TIMESTAMP_SPEC.md`, `PQC_SPEC.md`, `ADDRESS_SPEC.md`, `SERIALIZATION_SPEC.md`, `NETWORK_SPEC.md`, `GENESIS_SPEC.md`. |
| **Genesis Generation** | **VERIFIED** | Solved with 100% public inputs (`scripts/mine_qty4_genesis.py`), verified dual-path (`scripts/verify_qty4_genesis_dual_path.py`), public manifest in `genesis/public/`. |
| **Post-Quantum Cryptography** | **VERIFIED** | NIST FIPS 204 ML-DSA (`libqtydilithium`). Zero pseudo-crypto fallback tolerance. Domain separation `b"QUANTYCOIN_QTY4_PQC_SIGHASH_V1"`. |
| **Dual Proof-of-Work** | **VERIFIED** | Lane A (SHA256D ASIC) & Lane B (Scrypt 1024 General Purpose) independent mining & validation. |
| **Thermodynamic Chainwork** | **VERIFIED** | Mathematical work weights ($W_A=1, W_B=2048$), fork choice strictly resolves on cumulative work. |
| **Consensus Engine** | **VERIFIED** | Independent per-lane LWMA-1 retargeting, 120s per lane, 60s combined network target. Strict compact target decoding. |
| **Chainstate & UTXO** | **VERIFIED** | UTXO tracking, block connect/disconnect, and deep reorg verified across dual-PoW branches. |
| **Mempool** | **VERIFIED** | Mempool validation, PQC transaction support, and synchronization verified in test suite. |
| **P2P Network** | **VERIFIED** | Full-mesh multi-node P2P relay verified across nodes on port 19444 with magic `0x51545934`. |
| **Stratum V1 Server** | **VERIFIED** | Native Stratum V1 server in `miner/stratum.py` tested on port 3333 for pool mining. |
| **Stratum V2 Server** | **VERIFIED** | Native Stratum V2 binary framing (port 3334) with dual-lane multiplexing and low latency. |
| **Wallet & Multi-Sig PQC** | **VERIFIED** | HD wallet generating and spending classical, pure ML-DSA, and hybrid UTXOs with automated migration. |
| **RPC Server** | **VERIFIED** | Port 19445 JSON-RPC 2.0 with dual-PoW, chainwork, PQC, and migration RPC methods. |
| **Desktop Applications** | **VERIFIED** | Native Qt6 Node, Wallet, Miner, and Suite applications updated to QTY4. |
| **Brand System & Assets** | **VERIFIED** | Complete vector (`/brand/` SVGs) and raster preview assets generated and documented. |
| **Test Vector Corpus** | **VERIFIED** | 25 JSON test vector files in `tests/vectors/qty4/`. |
| **Adversarial Hardening** | **VERIFIED** | 10 attack vectors verified in `tests/test_adversarial_qty4.py`. |
| **Dual-PoW Simulation** | **VERIFIED** | 3 scenarios verified in `tests/test_dualpow_security_simulation.py`. |
| **Completion Gate** | **PASS** | 100% verified across all mandatory contract checkpoints. |
| **Protocol Truth Gate** | **VERIFIED** | `scripts/verify_protocol_truth.py` cross-checks all 6 `spec/qty4/*.json` vs runtime constants (2026-09-05 local PASS). |
| **Reference Differential** | **VERIFIED** | Stdlib-only `reference/qty4_reference.py` vs `core/` agreement in `tests/test_reference_differential_qty4.py` (10/10 PASS). |
| **Fuzz Smoke** | **VERIFIED** | Seeded bounded `tests/test_fuzz_qty4.py` over headers/compact/tx/address/P2P/SV2/varint + differential fuzz (PASS). |
| **Supply Chain** | **VERIFIED** | `scripts/generate_sbom.py` (CI artifact), Dependabot weekly, CodeQL python analysis. |
