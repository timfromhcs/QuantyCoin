# QuantyCoin Technical Roadmap

**Standard**: Evidence-Gated Progression. Milestones are marked complete only upon reproducible verification.  
**Active Protocol**: QTY4 (`70040`)  

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
- [x] **Thermodynamic Cumulative Chainwork**: Canonical fork choice determined strictly by accumulated energy ($W_A=1, W_B=2048$), defeating low-difficulty grinding attacks.
- [x] **Stratum V2 Binary Engine**: 6-byte binary framing on port 3334 (`SV2_DEFAULT_PORT`) with dual-lane channel multiplexing and low-latency PrevHash.
- [x] **Legacy UTXO Quantum Audit & Automated Migration**: Sovereign wallet tooling auditing vulnerable Secp256k1 coins and generating one-click migration transactions to ML-DSA (`qty1p...`) or Hybrid (`qty1z...`) addresses.
- [x] **Adversarial Test Suite**: Rigorous verification against synthetic signatures, malleated keys, cross-mode replay, and rented-GPU spam.

---

## Phase 3: QTY4 Consensus Rebuild & Formal Assurance (COMPLETED :white_check_mark:)

- [x] **Pure 64-Bit Integer Arithmetic**: Total elimination of floating-point arithmetic from monetary and subsidy calculations (`core.money.Amount`).
- [x] **Strict Compact Target Decoding**: Zero-tolerance bounds checking rejecting negative sign bits, zero mantissas, and exponent overflows.
- [x] **12-Stage Consensus Validation Pipeline**: Implementation of formal `core.validation` engine separating block validation stages.
- [x] **Public Genesis Sovereign Launch**: Generation of fresh, unmined public genesis block with 100% public inputs and dual-path reproducibility.
- [x] **Consensus Vector Corpus**: Generation and automated testing of 25 comprehensive JSON test vectors.
- [x] **Adversarial Hardening**: Rigorous 10-vector hostile test harness confirming atomic state rollback and parser robustness.

---

## Phase 4: Network Maturation & Ecosystem Scaling (ACTIVE :construction:)

- [ ] **Public DNS Seed Nodes**: Deployment of geo-distributed seed infrastructure for zero-configuration bootstrap.
- [ ] **Lightweight SPV Client Protocol**: Compact block filter serving (BIP157/BIP158) for mobile wallets.
- [ ] **Automated Multi-Platform Release Binaries**: Continuous CI artifact generation (Windows installer, Portable zip, Debian `.deb`, AppImage, Tarball).
- [ ] **Public Testnet (TQUA)**: Public multi-party testnet deployment on ports 29444 / 29445.
- [ ] **Native Compiled Node Kernel**: High-performance compiled consensus validation daemon for multi-gigabit throughput.
