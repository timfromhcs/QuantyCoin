# QuantyCoin (QTY) v2.2.0 — Autonomous Quantum-Resistant Blockchain

<p align="center">
  <img src="https://img.shields.io/badge/QuantyCoin-v2.2.0-blue.svg?style=for-the-badge&logo=bitcoin" alt="QuantyCoin Version" />
  <img src="https://img.shields.io/badge/Consensus-32MB%20Blocks-green.svg?style=for-the-badge" alt="32MB Blocks" />
  <img src="https://img.shields.io/badge/Fee%20Split-50%2F50%20Treasury-yellow.svg?style=for-the-badge" alt="50/50 Fee Split" />
  <img src="https://img.shields.io/badge/Airdrop-Monthly%20Autonomous-red.svg?style=for-the-badge" alt="Monthly Airdrop" />
  <img src="https://img.shields.io/badge/Security-ML--DSA%20Post--Quantum-purple.svg?style=for-the-badge" alt="ML-DSA Post-Quantum" />
  <img src="https://img.shields.io/badge/Mining-SHA--256%20ASIC-orange.svg?style=for-the-badge" alt="SHA-256 Mining" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?style=for-the-badge" alt="MIT License" />
</p>

---

## 🚀 Overview & What's New in v2.2.0

**QuantyCoin (QTY) v2.2.0** is an autonomous, quantum-resistant cryptocurrency platform engineered for high-throughput scaling, community reward distribution, and light client usability.

### 🌟 Key Upgrades & Hotfixes in v2.2.0
- 🔧 **Multi-Platform CI/CD Fix**: Resolved Automake Makefile dependencies and permissions for Linux, macOS, and MinGW Windows builds.
- 💰 **50/50 Transaction Fee Split**: 50% of every transaction fee goes to the miner; 50% goes to the Community Treasury Donation Wallet (`qty1qspendenwallettreasury2026`).
- 🪂 **Autonomous Monthly Airdrop Engine**: Treasury funds accumulated each month (~43,200 blocks) are distributed equally to all registered wallets holding **> 5 QTY** with an age **>= 21 days (3 weeks)**.
- 🌐 **Standalone Light Client Mode**: Wallet (`qty-qt`) and Miner operate seamlessly without requiring a local full node daemon by automatically connecting to the best online seed node with instant failover.
- 🔍 **Integrated Block Explorer & Node GUI**: Query blocks, merkle roots, transaction fees, and node health in real-time.
- 🔑 **Simplified GUI Wallet & 24-Word Recovery**: New wallet wizard, seed phrase restoration, file backup import, and session auto-login.

---

## 📊 Core Network Specifications

| Parameter | Mainnet Value | Description |
| :--- | :--- | :--- |
| **Version** | `v2.2.0` | Release Version |
| **Ticker Symbol** | `QTY` | Currency Ticker |
| **Address Formats** | `qty1...` / `dqty1...` | Bech32 & Dilithium P2QRH Native |
| **Block Capacity** | **32 MB** (`33,554,432 bytes`) | High-Throughput Scaling |
| **Target Block Interval** | **60 Seconds** (1 Minute) | Fast Finality |
| **Mining Algorithm** | **SHA-256 (ASIC Compatible)** | Hardened PoW Baseline |
| **Fee Split Ratio** | **50% Miner / 50% Treasury** | Automatic Treasury Funding |
| **Treasury Address** | `qty1qspendenwallettreasury2026` | Community Donation Treasury |
| **Airdrop Frequency** | Every ~43,200 Blocks (~30 Days) | Monthly Equal Share Distribution |
| **Airdrop Eligibility** | Balance > 5 QTY & Age >= 21 Days | Anti-Sybil Proof of Age & Balance |
| **Difficulty Algorithm** | **DGW / LWMA** (Height 1) | Instant Dynamic Retargeting |
| **Signature Scheme** | **ML-DSA-65** | NIST Post-Quantum Standard |
| **P2P Port / RPC Port** | `19333` / `18332` | Network Ports |

---

## 🛠️ Building & Running QuantyCoin v2.2.0

```bash
# Automated Build (Linux / macOS)
./scripts/build_quantycoin.sh

# Run Block Explorer
python3 ./scripts/explorer.py 0

# Run Airdrop Registrar / Registration
python3 ./scripts/start_airdrop_registrar.py register "qty1qa8639f6b36aa83d174f6ff8f608084a9475678b1" 10 30

# Start Full Node
./scripts/start_node.sh

# Start Automated Miner
./scripts/start_miner.sh
```

---

## 📦 Releases & GitHub Actions

Automated continuous integration builds for Linux, macOS, and Windows are compiled via [.github/workflows/build.yml](.github/workflows/build.yml). Download pre-compiled binary packages from [GitHub Releases](https://github.com/timfromhcs/QuantyCoin/releases/tag/v2.2.0).

---

## 📄 License

QuantyCoin Core is licensed under the terms of the **MIT License**. See [COPYING](COPYING) for details.
