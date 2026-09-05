# QuantyCoin Technical Roadmap

**Standard**: Evidence-Gated Progression. Milestones are marked complete only upon reproducible verification.

---

## Phase 1: Protocol Rebuild & Consensus Freeze (COMPLETED :white_check_mark:)

- [x] **Air-Gapped Genesis Block**: Generated in local secret vault, independently verified, and frozen.
- [x] **Consensus Engine**: SHA-256D Proof-of-Work, 60s block times, 32 MB max block size, LWMA-1 difficulty retargeting.
- [x] **Chainstate & UTXO Engine**: Atomic block apply/disconnect with verified 10-block deep reorganization recovery.
- [x] **Mempool Engine**: In-memory conflict detection, fee sorting, and double-spend rejection under load.
- [x] **Binary P2P Network**: Full-mesh gossip protocol with wire framing and peer exchange.
- [x] **Stratum V1 Mining Pool**: Socket server on port 3333 supporting ASIC/GPU miner subscriptions and share submission.
- [x] **BIP39/44 HD Wallet**: 24-word seed generation, Bech32 native witness address encoding (`qty1q...`).
- [x] **Threaded JSON-RPC 2.0**: Concurrency server supporting full node, mining, and wallet APIs.
- [x] **Native Desktop Applications**: Qt6 GUI suite for Node, Sovereign Wallet, Miner, and Master Suite.
- [x] **Comprehensive Test Suite**: Unit, functional, reorg, and stress test matrix passing at 100%.

---

## Phase 2: Network Maturation & Tooling (ACTIVE :construction:)

- [ ] **Public DNS Seed Nodes**: Deployment of geo-distributed seed infrastructure for zero-configuration bootstrap.
- [ ] **Lightweight SPV Client Protocol**: Compact block filter serving (BIP157/BIP158) for mobile wallets.
- [ ] **Automated Release Binaries**: Continuous multi-platform artifact generation (Windows installer, Debian `.deb`, AppImage, macOS `.dmg`).
- [ ] **Public Testnet (TQUA)**: Public multi-party testnet deployment on ports 29888 / 29889.

---

## Phase 3: Advanced Cryptography & Research (PLANNED :telescope:)

- [ ] **Post-Quantum Signature Verification**: Completion and formal audit of CRYSTALS-Dilithium (ML-DSA) C++ integration.
- [ ] **Stratum V2 Binary Framing**: Direct miner communication, encrypted channels, and decentralized job negotiation.
- [ ] **Native Compiled Node Kernel**: High-performance Rust / C++ consensus validation daemon for multi-gigabit throughput.
