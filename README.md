# QuantyCoin (QTY) v2.3.0 — Autonomous Quantum-Resistant Blockchain

<p align="center">
  <img src="https://img.shields.io/badge/QuantyCoin-v2.3.0-blue.svg?style=for-the-badge&logo=bitcoin" alt="QuantyCoin Version" />
  <img src="https://img.shields.io/badge/Platforms-Linux%20%7C%20Windows%20%7C%20macOS%20%7C%20Android-brightgreen.svg?style=for-the-badge" alt="Platforms" />
  <img src="https://img.shields.io/badge/Consensus-32MB%20Blocks-green.svg?style=for-the-badge" alt="32MB Blocks" />
  <img src="https://img.shields.io/badge/Fee%20Split-50%2F50%20Treasury-yellow.svg?style=for-the-badge" alt="50/50 Fee Split" />
  <img src="https://img.shields.io/badge/Airdrop-Monthly%20Autonomous-red.svg?style=for-the-badge" alt="Monthly Airdrop" />
  <img src="https://img.shields.io/badge/Security-ML--DSA%20Post--Quantum-purple.svg?style=for-the-badge" alt="ML-DSA Post-Quantum" />
  <img src="https://img.shields.io/badge/Mining-SHA--256%20ASIC-orange.svg?style=for-the-badge" alt="SHA-256 Mining" />
</p>

---

## 🚀 Overview & What's New in v2.3.0

**QuantyCoin (QTY) v2.3.0** is an autonomous, quantum-resistant cryptocurrency platform engineered for high-throughput scaling, community reward distribution, and multi-platform light client usability.

### 🌟 Key Upgrades & Hotfixes in v2.3.0
- 📱 **Android Wallet Support**: Built-in Android Light Client Wallet package workflow (`quantycoin-android-wallet.zip`) for standalone mobile transactions and seed phrase restoration.
- 🔧 **C++ Header Fix in `src/node/miner.cpp`**: Added missing `#include <util/strencodings.h>` resolving the `ParseHex` undeclared identifier error on Linux & macOS compilers.
- 🍎 **macOS Build Hardening**: Fixed Homebrew `qt@5` environment variables (`PATH` and `PKG_CONFIG_PATH`) for seamless Qt5 macOS compilation.
- 💰 **50/50 Transaction Fee Split**: 50% of every transaction fee goes to the miner; 50% goes to the Community Treasury Donation Wallet (`qty1qspendenwallettreasury2026`).
- 🪂 **Autonomous Monthly Airdrop Engine**: Treasury funds accumulated each month (~43,200 blocks) are distributed equally to all registered wallets holding **> 5 QTY** with an age **>= 21 days (3 weeks)**.
- 🌐 **Standalone Light Client Mode**: Wallet (`qty-qt`) and Miner operate seamlessly without requiring a local full node daemon by automatically connecting to the best online seed node with instant failover.

---

## 📊 Core Network Specifications

| Parameter | Mainnet Value | Description |
| :--- | :--- | :--- |
| **Version** | `v2.3.0` | Release Version |
| **Ticker Symbol** | `QTY` | Currency Ticker |
| **Supported Platforms** | Linux x86_64, Windows MinGW, macOS x86_64, Android | Multi-Platform Binaries |
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

---

## 🛠️ Building & Running QuantyCoin v2.3.0

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

Automated continuous integration builds for Linux, macOS, Windows, and Android are compiled via [.github/workflows/build.yml](.github/workflows/build.yml). Download pre-compiled binary packages from [GitHub Releases](https://github.com/timfromhcs/QuantyCoin/releases/tag/v2.3.0).

---

## 📄 License

QuantyCoin Core is licensed under the terms of the **MIT License**. See [COPYING](COPYING) for details.
