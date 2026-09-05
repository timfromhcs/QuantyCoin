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

## Phase 2: Post-Quantum Security & Dual-PoW Consensus (COMPLETED :white_check_mark:)

- [x] **NIST FIPS 204 ML-DSA Transaction Authorization**: Zero mock crypto, native C lattice acceleration (`libqtydilithium`), fail-closed verification.
- [x] **Asymmetric Dual-PoW Mining**: Lane A (SHA-256D ASIC) and Lane B (RFC 7914 Scrypt General Purpose) with independent LWMA-1 difficulty adjustment.
- [x] **Thermodynamic Cumulative Chainwork**: Canonical fork choice determined strictly by accumulated energy, defeating low-difficulty grinding attacks.
- [x] **Stratum V2 Binary Engine**: 6-byte binary framing on port 3334 (`SV2_DEFAULT_PORT`) with dual-lane channel multiplexing and low-latency PrevHash.
- [x] **Legacy UTXO Quantum Audit & Automated Migration**: Sovereign wallet tooling auditing vulnerable Secp256k1 coins and generating one-click migration transactions to ML-DSA (`qty1p...`) or Hybrid (`qty1z...`) addresses.
- [x] **Adversarial Test Suite**: Rigorous verification against synthetic signatures, malleated keys, cross-mode replay, and rented-GPU spam.

---

## Phase 3: Network Maturation & Ecosystem Scaling (ACTIVE :construction:)

- [ ] **Public DNS Seed Nodes**: Deployment of geo-distributed seed infrastructure for zero-configuration bootstrap.
- [ ] **Lightweight SPV Client Protocol**: Compact block filter serving (BIP157/BIP158) for mobile wallets.
- [ ] **Automated Multi-Platform Release Binaries**: Continuous CI artifact generation (Windows installer, Debian `.deb`, AppImage, macOS `.dmg`).
- [ ] **Public Testnet (TQUA)**: Public multi-party testnet deployment on ports 29888 / 29889.
- [ ] **Native Compiled Node Kernel**: High-performance compiled consensus validation daemon for multi-gigabit throughput.

