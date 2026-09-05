# QuantyCoin 2.0 (QTY2) Autonomous Rebuild State

**Branch**: `v2.0`  
**Current Phase**: Phase 5 — NIST FIPS 204 PQC, Dual-PoW Consensus & Native Stratum V2 Protocol (QUANTYCOIN-QTY2-PQC-DUALPOW-SV2-2026)  
**Protocol Version**: QTY2 (70020)  
**Last Updated**: 2026-09-05  

---

## Subsystem Status Matrix

| Subsystem | Status | Notes |
| :--- | :--- | :--- |
| **Agent State & Policy** | **VERIFIED** | `AGENTS.md` active, `docs/agent/` state files continuously maintained. |
| **Local Secret Vault** | **VERIFIED** | Local air-gapped secret vault structure operational outside git. |
| **Zero-Leak Git Policy** | **VERIFIED** | Enforced by `.gitignore` and verified by `scripts/verify_security.py`. |
| **Protocol Freeze & Specs**| **VERIFIED** | Frozen specs: `PQC_SPEC.md`, `DUAL_POW_SPEC.md`, `CHAINWORK_SPEC.md`, `STRATUM_V2_SPEC.md`, `MIGRATION_SPEC.md`. |
| **Genesis Generation** | **VERIFIED** | Solved, verified, and exported to `genesis/PUBLIC_GENESIS_MANIFEST.json`. |
| **Post-Quantum Cryptography** | **VERIFIED** | NIST FIPS 204 ML-DSA-65 (`libqtydilithium`), Hybrid mode, Bech32m witness v1/v2 (`qty1p...`, `qty1z...`). |
| **Dual Proof-of-Work** | **VERIFIED** | Lane A (SHA256D ASIC) & Lane B (Scrypt 1024 General Purpose) independent mining & validation. |
| **Thermodynamic Chainwork** | **VERIFIED** | Mathematical work weights ($W_A=1, W_B=2048$), fork choice resolves on cumulative work. |
| **Consensus Engine** | **VERIFIED** | Independent per-lane LWMA-1 retargeting, 120s per lane, 60s combined network target. |
| **Chainstate & UTXO** | **VERIFIED** | UTXO tracking, block connect/disconnect, and deep reorg verified across dual-PoW branches. |
| **Mempool** | **VERIFIED** | Mempool validation, PQC transaction support, and synchronization verified in test suite. |
| **P2P Network** | **VERIFIED** | Full-mesh multi-node P2P relay verified across nodes. |
| **Stratum V1 Server** | **VERIFIED** | Native Stratum V1 server in `miner/stratum.py` tested for pool mining. |
| **Stratum V2 Server** | **VERIFIED** | Native Stratum V2 binary framing (port 3334) with dual-lane multiplexing and low latency. |
| **Wallet & Multi-Sig PQC** | **VERIFIED** | HD wallet generating and spending classical, pure ML-DSA-65, and hybrid UTXOs. |
| **RPC Server** | **VERIFIED** | Added `getmininglanes`, `getminingtargets`, `getchainwork`, `getnewpqaddress`, `getaddressinfo`, `getstratuminfo`. |
| **Desktop Applications** | **VERIFIED** | Native Qt6 Node, Wallet, Miner, and Suite applications updated to QTY2 2.0.0. |
| **Brand System & Assets** | **VERIFIED** | Complete vector (`/brand/` SVGs) and raster preview assets generated and documented. |
| **Testing & CI/CD** | **VERIFIED** | Complete test runner passing with 100% success (0 failures). |
| **Completion Gate** | **PASS** | 100% verified across all mandatory contract checkpoints. |
