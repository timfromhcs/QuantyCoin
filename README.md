# QuantyCoin (QTY) — Autonomous Quantum-Resistant Blockchain

<p align="center">
  <img src="https://img.shields.io/badge/QuantyCoin-v1.0.0-blue.svg?style=for-the-badge&logo=bitcoin" alt="QuantyCoin Version" />
  <img src="https://img.shields.io/badge/Consensus-32MB%20Blocks-green.svg?style=for-the-badge" alt="32MB Blocks" />
  <img src="https://img.shields.io/badge/Security-ML--DSA%20Post--Quantum-purple.svg?style=for-the-badge" alt="ML-DSA Post-Quantum" />
  <img src="https://img.shields.io/badge/Mining-SHA--256%20ASIC-orange.svg?style=for-the-badge" alt="SHA-256 Mining" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?style=for-the-badge" alt="MIT License" />
</p>

---

## 🚀 Overview

**QuantyCoin (QTY)** is an autonomous, quantum-resistant cryptocurrency platform engineered for ultra-high throughput and long-term cryptographic immutability. Built upon post-quantum signature schemes (**ML-DSA**) and **P2QRH** address encodings, QuantyCoin guards financial state against quantum computer attacks while scaling baseline block capacity to **32 MB per minute**.

QuantyCoin retains **SHA-256 Proof of Work (PoW)**, maintaining full hardware compatibility with existing ASIC infrastructure while deploying **Dark Gravity Wave (DGW) / LWMA** difficulty retargeting to ensure smooth 60-second block production.

---

## 📊 Core Network Specifications

| Parameter | Mainnet Value | Notes |
| :--- | :--- | :--- |
| **Coin Name** | QuantyCoin | Official Network Name |
| **Ticker Symbol** | `QTY` | Display Ticker |
| **Address Formats** | `qty1...` / `dqty1...` | Bech32 & Dilithium P2QRH Native |
| **Block Capacity** | **32 MB** (`33,554,432 bytes`) | High-Throughput Scaling |
| **Target Block Interval** | **60 Seconds** (1 Minute) | Fast Finality |
| **Mining Algorithm** | **SHA-256 (ASIC Compatible)** | Hardened PoW Baseline |
| **Difficulty Algorithm** | **DGW / LWMA** (Height 1) | Instant Dynamic Adjustment |
| **Halving Interval** | 2,100,000 Blocks (~4 Years) | Predictable Emission Schedule |
| **Signature Scheme** | **ML-DSA-65** | NIST Post-Quantum Standard |
| **P2P Port** | `19333` | Peer-to-Peer Network Port |
| **RPC Port** | `18332` | JSON-RPC Interface Port |
| **Magic Bytes** | `0xAE`, `0xCF`, `0x12`, `0x45` | P2P Network Header Bytes |

---

## 🛡️ Quantum Resistance & Cryptography

QuantyCoin replaces legacy ECDSA (secp256k1) keypairs with **ML-DSA (Module-Lattice Digital Signature Algorithm)**, preventing quantum Shor's algorithm attacks.

- **P2QRH (Pay-to-Quantum-Resistant-Hash)** address structure (`qty1...` & `dqty1...`).
- Fully Segregated Witness (SegWit) integration for post-quantum signature payloads.
- Complete UTXO quantum safety from genesis block height 1.

---

## 🌐 Network & P2P Resiliency

QuantyCoin features a multi-tiered connection stack designed for maximum uptime and zero-configuration networking:

1. **Automatic Port Mapping**: Built-in **UPnP / NAT-PMP** protocol support (`--enable-upnp-default`).
2. **Dual-Stack IP**: Native IPv4 and IPv6 network listener support.
3. **Anonymity Proxies**: Native SOCKS5 proxy support for **Tor** and **I2P** routing.
4. **Seed Nodes**: Pre-configured global bootstrap seeds (`seed1.quantycoin.org`, `seed2.quantycoin.org`).

---

## 🖥️ Graphical User Interface (GUI Suite)

QuantyCoin includes a native Qt5 desktop application suite providing:

- 💼 **GUI Wallet (`quantycoin-qt`)**: Send, receive, encrypt, and back up ML-DSA post-quantum funds.
- ⛏️ **Integrated GUI Miner**: One-click CPU/RPC mining toggle within the interface.
- 📡 **Node Monitor**: Real-time peer connections, traffic graphs, and block height inspection.

---

## 🛠️ Building from Source

### 🐧 Linux (Ubuntu / Debian)

```bash
# Install required build dependencies
sudo apt-get update
sudo apt-get install -y build-essential libtool autotools-dev automake pkg-config \
  bsdmainutils python3 libssl-dev libevent-dev libboost-system-dev libboost-filesystem-dev \
  libboost-test-dev libboost-thread-dev libsqlite3-dev qtbase5-dev qttools5-dev-tools \
  libminiupnpc-dev libnatpmp-dev zip

# Clone and build QuantyCoin
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin
./autogen.sh
./configure --with-gui=qt5 --enable-upnp-default
make -j$(nproc)
```

### 🍎 macOS (Homebrew)

```bash
# Install dependencies via Homebrew
brew install automake libtool boost miniupnpc libevent pkg-config sqlite qt@5

# Build QuantyCoin
./autogen.sh
./configure --with-gui=qt5
make -j$(sysctl -n hw.ncpu)
```

### 🪟 Windows (Cross-compilation via MinGW / WSL)

```bash
# Inside Ubuntu WSL
sudo apt install -y g++-mingw-w64-x86-64 mingw-w64-x86-64-dev autoconf automake libtool pkg-config
cd QuantyCoin/depends
make HOST=x86_64-w64-mingw32 -j$(nproc)
cd ..
./autogen.sh
./configure --host=x86_64-w64-mingw32 --prefix=$(pwd)/depends/x86_64-w64-mingw32 --without-gui
make -j$(nproc)
```

---

## ⚡ Quick Start & Running Commands

### 1. Launching Full Node Daemon (`qtyd`)
```bash
./src/qtyd -daemon -upnp
```

### 2. Launching Desktop GUI (`qty-qt`)
```bash
./src/qt/qty-qt
```

### 3. Interacting via RPC CLI (`qty-cli`)
```bash
# Get blockchain info
./src/qty-cli getblockchaininfo

# Get network info & connected peers
./src/qty-cli getnetworkinfo

# Generate a new quantum-safe receive address
./src/qty-cli getnewaddress "" "bech32"
```

### 4. Mining QuantyCoin via RPC
```bash
# Mine 10 blocks to an address
./src/qty-cli generatetoaddress 10 "qty1qa8639f6b36aa83d174f6ff8f608084a9475678b1"
```

---

## 📦 Utility Scripts

Helper scripts are provided in the `scripts/` directory:

- 🚀 `scripts/build_quantycoin.sh`: Automated compilation script.
- 🌐 `scripts/start_node.sh`: Launch full node daemon.
- ⛏️ `scripts/start_miner.sh`: Launch automated RPC mining script.

---

## 📄 License & Legal

QuantyCoin Core is released under the terms of the **MIT License**. See [COPYING](COPYING) for details.
