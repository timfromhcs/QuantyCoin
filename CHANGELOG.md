# QuantyCoin Release Notes & Changelog

## [2.0.0] - 2026-08-16 — Major Consensus & Feature Upgrade

QuantyCoin v2.0.0 introduces groundbreaking consensus enhancements, automated community treasury fee splitting, autonomous monthly airdrops, standalone light client capabilities, and an integrated GUI suite.

### 🌟 New Features in v2.0.0

#### 1. 💰 50/50 Transaction Fee Split & Treasury Donation Wallet
- 50% of every transaction fee goes directly to the Miner who mined the block.
- 50% of every transaction fee goes to the **Community Treasury Donation Wallet** (`qty1qspendenwallettreasury2026`).

#### 2. 🪂 Autonomous Monthly Treasury Airdrop Engine
- Wallets holding **> 5 QTY** with an age **>= 21 days (3 weeks / 30,240 blocks)** can register for the monthly airdrop.
- Every **~43,200 blocks (~30 days)**, the entire accumulated monthly treasury balance is divided equally among all registered eligible participants.
- Equal share distribution (`treasury_balance / total_registered_participants`).

#### 3. 🌐 Standalone Light Client Mode (Wallet & Miner without local node)
- GUI Wallet (`qty-qt`) and GUI Miner can run without requiring a full local node daemon.
- Automatically queries and connects to the best online seed node (`seed1.quantycoin.org`, `seed2.quantycoin.org`).
- Automatic failover to backup seeds if a node disconnects.

#### 4. 🔍 Integrated Block Explorer & Node GUI Suite
- Integrated Block Explorer tool (`scripts/explorer.py`) for querying blocks, transactions, merkle roots, and difficulty.
- Node Monitor GUI tab for inspecting connected peers, network throughput, and sync progress.

#### 5. 🔑 Simplified Wallet Setup & 24-Word Recovery Wizard
- Create new wallets, restore wallets from 24-word seed phrases, or import backup wallet files.
- Session persistence: remembers logged-in identity automatically upon restart.

#### 6. ⛏️ Simplified One-Click GUI Miner
- One-click mining start/stop toggle in Qt GUI.
- Adjustable CPU thread slider with live hash rate monitoring.

---

## [1.0.0] - 2026-08-16 — Initial Launch
- Quantum-Resistant ML-DSA-65 signatures & P2QRH addresses (`qty` / `dqty`).
- 32 MB Block capacity & 1-minute block intervals.
- SHA-256 ASIC-compatible Proof of Work.
- Multi-platform CI/CD release pipeline for Linux, macOS, and Windows.
