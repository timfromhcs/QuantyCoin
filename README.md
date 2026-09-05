# QuantyCoin 2.0 (QTY2)

<div align="center">

<img src="brand/logo.svg" alt="QuantyCoin Logo" width="420" />

<br/>

[![CI](https://github.com/timfromhcs/QuantyCoin/actions/workflows/ci.yml/badge.svg)](https://github.com/timfromhcs/QuantyCoin/actions)
[![Protocol](https://img.shields.io/badge/protocol-QTY2%20(70020)-0284C7.svg)](docs/protocol/index.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-8A2BE2.svg)](LICENSE)
[![Verification](https://img.shields.io/badge/verification-evidence--gated-00FF88.svg)](VERIFICATION.md)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Security: Zero-Leak](https://img.shields.io/badge/security-zero--leak%20verified-00FF88.svg)](THREAT_MODEL.md)

<p align="center">
  <strong>An independent Dual-PoW Layer-1 cryptocurrency featuring SHA-256D ASIC and General-Purpose CPU/GPU mining lanes, NIST FIPS 204 ML-DSA-44 post-quantum transaction authorization, 60-second combined block intervals, thermodynamic cumulative chainwork, native Stratum V2 protocol, and self-sovereign Qt6 desktop applications.</strong>
</p>

</div>

---

## 📑 Table of Contents

1. [Honest Status](#1-honest-status)
2. [Why QuantyCoin?](#2-why-quantycoin)
3. [Verified Features](#3-verified-features)
4. [Experimental Features](#4-experimental-features)
5. [Planned Features](#5-planned-features)
6. [Quickstart & Onboarding](#6-quickstart--onboarding)
7. [System Architecture](#7-system-architecture)
8. [Consensus Rules & Protocol Parameters](#8-consensus-rules--protocol-parameters)
9. [Air-Gapped Genesis Block](#9-air-gapped-genesis-block)
10. [Mining & Stratum Mining Setup](#10-mining--stratum-mining-setup)
11. [Sovereign Wallet & Desktop Applications](#11-sovereign-wallet--desktop-applications)
12. [Automated Testing & Independent Verification](#12-automated-testing--independent-verification)
13. [Release Management](#13-release-management)
14. [Security & Threat Model](#14-security--threat-model)
15. [Roadmap](#15-roadmap)
16. [Contributing](#16-contributing)
17. [Citation & License](#17-citation--license)

---

## 1. Honest Status

QuantyCoin QTY3 adheres to strict, evidence-based technical claims:

- **Consensus State**: **FROZEN & VERIFIED**. The production Genesis block hash (`00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`) is locked with mandatory runtime assertions in [`node/chainstate.py`](node/chainstate.py).
- **Authoritative Stack**: The operational protocol engine is the native Python stack (`core/`, `crypto/`, `network/`, `node/`, `wallet/`, `miner/`, `ui/`) with native C acceleration for NIST FIPS 204 ML-DSA (`libqtydilithium`).
- **Throughput Reality**: Target block interval is 60 seconds (120s per lane interleaved) with an upper block capacity limit of 32 MB. Tested single-threaded mempool ingestion is 16 transactions/sec (500 TX burst verified in 32s). Theoretical baseline PoW throughput for standard transactions is approximately 14–28 TPS on 1 MB equivalent payloads, scaling linearly under larger block templates. We do not make unsubstantiated "thousands of TPS" marketing claims.
- **Cryptographic Security**: Mainnet Layer-1 supports three transaction authorization modes: `LEGACY_ECDSA` (Secp256k1), `HYBRID` (Secp256k1 + NIST FIPS 204 ML-DSA-44), and `ML_DSA` (Pure NIST FIPS 204 ML-DSA-44). Insecure pseudo-cryptographic fallbacks are strictly barred (fail-closed consensus via `CryptographicBackendUnavailableError`).
- **Dual-PoW Liveness**: Lane A (`SHA256D_ASIC`) and Lane B (`GENERAL_PURPOSE` Scrypt 1024) independently sustain chain progression under partitioned LWMA-1 retargeting ($N=45$).
- **Air-Gap Security**: All sensitive Genesis generation materials, private nonces, and uncompressed keys are completely isolated in an external air-gapped vault outside git version control.

---

## 2. Why QuantyCoin?

- **ASIC-Compatible SHA-256D PoW**: Operates on pure double-SHA256 Proof-of-Work, providing compatibility with standard mining infrastructure and hardware.
- **60-Second Block Interval**: Provides frequent confirmation progress while preserving Proof-of-Work probabilistic finality.
- **Oscillation-Free LWMA-1 Retargeting**: Linear-Weighted Moving Average recalculates target difficulty on every block across a 45-block window, absorbing hashrate fluctuations smoothly.
- **Native Stratum V1 Pool Engine**: Directly hosts an ASIC-ready Stratum mining pool on TCP port `3333` without third-party proxy daemons.
- **Complete Self-Sovereignty**: Bundles full node, wallet, miner, and telemetry into clean Qt6 desktop suites.

---

## 3. Verified Features

Every feature listed below is verified by automated, executable test suites:

| Feature / Capability | Classification | Direct Evidence Location |
| :--- | :--- | :--- |
| **SHA-256D ASIC Mining (Lane A)** | **VERIFIED** | `core/block.py`, `tests/test_pqc_dualpow_sv2.py` |
| **CPU/GPU Scrypt Mining (Lane B)** | **VERIFIED** | `core/block.py`, `tests/test_pqc_dualpow_sv2.py` |
| **Thermodynamic Cumulative Chainwork**| **VERIFIED** | `node/chainstate.py`, `docs/protocol/CHAINWORK_SPEC.md` |
| **NIST FIPS 204 ML-DSA-44 Signatures**| **VERIFIED** | `crypto/mldsa.py`, `tests/test_pqc_dualpow_sv2.py` |
| **Hybrid Bech32m Authorization** | **VERIFIED** | `core/transaction.py`, `tests/test_pqc_dualpow_sv2.py` |
| **Stratum V2 Binary Engine** | **VERIFIED** | `miner/stratum_v2.py`, `tests/test_pqc_dualpow_sv2.py` |
| **Air-Gapped Genesis Block** | **VERIFIED** | `genesis/PUBLIC_GENESIS_MANIFEST.json` |
| **LWMA-1 Per-Lane Retargeting** | **VERIFIED** | `core/consensus.py`, `tests/test_pqc_dualpow_sv2.py` |
| **UTXO Chainstate & Deep Reorgs**| **VERIFIED** | `core/utxo.py`, `tests/test_functional_reorg.py` |
| **Full Mesh P2P Wire Relay** | **VERIFIED** | `network/p2p_server.py`, `tests/test_functional_p2p.py` |
| **Stratum V1 Mining Pool Server** | **VERIFIED** | `miner/stratum.py`, `tests/test_functional_stratum.py` |
| **BIP39/44 Multi-Mode HD Wallet** | **VERIFIED** | `wallet/hd_wallet.py`, `tests/test_functional_wallet.py` |
| **Threaded JSON-RPC 2.0 Engine** | **VERIFIED** | `node/rpc_server.py`, `tests/test_framework.py` |
| **Native Qt6 Desktop Applications**| **VERIFIED** | `ui/`, `quanty_suite_app.py` |

---

## 4. Experimental Features

The following components represent active research and development:

- **C++ Dilithium Integration**: An experimental C++ research fork of Bitcoin Knots exploring post-quantum CRYSTALS-Dilithium signature schemes (`src/crypto/dilithium/`, tracked in [`docs/security/AUDIT_REMEDIATION_VERIFICATION.md`](docs/security/AUDIT_REMEDIATION_VERIFICATION.md)).
- **Compact Block Filters (BIP 157/158)**: Prototype client-side filtering engine for lightweight SPV synchronization.

---

## 5. Planned Features

Future milestones scheduled in [`ROADMAP.md`](ROADMAP.md):

- **Hardware Wallet Integration**: USB HID interface for Ledger and Trezor hardware devices.
- **Multi-Signature P2WSH Script Builder**: Native UI for threshold m-of-n multi-signature custody.
- **Native Compiled Node Kernel**: High-performance compiled daemon for multi-gigabit throughput.


---

## 6. Quickstart & Onboarding

### 1. Prerequisites & Installation
```bash
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin

# Install runtime and GUI dependencies
pip install PySide6 qrcode pillow
```

### 2. Launch the Full Node Daemon
```bash
python quantyd_cli.py
```

### 3. Launch the Sovereign Desktop Wallet
```bash
python quanty_wallet_full_app.py
```

### 4. Detailed Onboarding Guides
- [End-User Guide](docs/USER_GUIDE.md): Wallet management, backup, and transactions.
- [Miner & Pool Guide](docs/MINER_GUIDE.md): Solo mining, worker threads, and Stratum configuration.
- [Developer Guide](docs/DEVELOPER_GUIDE.md): Protocol architecture, consensus modules, and test framework.

---

## 7. System Architecture

```mermaid
graph TB
    subgraph P2P ["P2P Wire Network (Port 19888)"]
        direction TB
        MGR[P2P Server & Wire Framing]
        PEERS[Inbound & Outbound Peer Sockets]
        MGR <-->|Magic: 0x5155414E| PEERS
    end

    subgraph CORE ["Core Node Daemon (quantyd)"]
        CS[Chainstate & Fork-Choice Engine]
        UTXO[UTXO State Machine & Undo Log]
        MEM[Mempool Engine & Fee Sorter]
        RPC[Threaded JSON-RPC Server\nPort 19889]

        MGR -->|inv / block / tx| CS
        CS -->|Connect / Disconnect| UTXO
        MEM -->|Validate UTXO Spend| UTXO
        CS -->|Evict Mined Tx| MEM
        RPC <-->|Query & Broadcast| CS
        RPC <-->|Submit Raw Tx| MEM
    end

    subgraph MINING ["Mining Infrastructure (Port 3333)"]
        STRATUM[Stratum V1 Pool Server]
        ENG[Authoritative Mining Engine]
        STRATUM <-->|Get Block Template| RPC
        ENG <-->|Submit Mined Block| RPC
    end

    subgraph WALLET ["Wallet & Desktop GUIs (Qt6)"]
        HD[BIP39/44 HD Wallet]
        GUI_W[Sovereign Wallet GUI]
        GUI_N[Node Explorer GUI]
        GUI_M[Miner Telemetry GUI]
        GUI_S[Combined Master Suite]

        HD -->|Sign Tx| RPC
        GUI_W <-->|Balance & History| RPC
        GUI_N <-->|Peer Telemetry| RPC
        GUI_M <-->|Hashrate Stream| STRATUM
        GUI_S -->|Unified Control| RPC
    end
```

---

## 8. Consensus Rules & Protocol Parameters

| Parameter | Mainnet Specification | Technical Consensus Rule |
| :--- | :--- | :--- |
| **Protocol Version** | `70020` | Handshake version identifier (`PROTOCOL_VERSION`) |
| **Chain Identifier** | `quantycoin-2.0` | Unique network identifier (`CHAIN_ID`) |
| **Wire Magic Bytes** | `0x51 0x55 0x41 0x4E` | ASCII `"QUAN"` framing delimiter |
| **Target Block Interval**| `60 seconds` | Cadence for Poisson difficulty retargeting |
| **Difficulty Algorithm** | **LWMA-1** | Window: 45 blocks, bounded oscillation clamping |
| **Max Block Size** | `32 MB` (33,554,432 bytes) | Upper bound on serialized block length |
| **Initial Block Reward** | `50.00 QTY` | $5,000,000,000$ Satoshis |
| **Halving Interval** | `2,100,000 blocks` | Halving occurs approximately every 4 years |
| **Max Supply Cap** | `21,000,000 QTY` | Finite supply ceiling ($2.1 \times 10^{15}$ Satoshis) |
| **Coinbase Maturity** | `100 blocks` | Mined outputs spendable after 100 confirmations |
| **Address Encodings** | **Bech32 & Base58Check** | Native witness v0 (`qty1q...`) & legacy (`Q...`) |
| **Default Ports** | P2P: `19888` &bull; RPC: `19889` &bull; Stratum: `3333` | Dedicated independent network ports |

---

## 9. Air-Gapped Genesis Block

The QuantyCoin 2.0 Genesis block was verifiably mined in an air-gapped environment:

- **Genesis Hash**: `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`
- **Merkle Root**: `ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f`
- **Timestamp**: `1788600000` (*"2026-09-05: QuantyCoin 2.0 - SHA256D Layer-1 Autonomous Blockchain Protocol"*)
- **Nonce**: `333641`
- **Bits**: `0x1e0fffff` (`504365055`)
- **Payout Address**: `qty1qh46xnlu649ug0yfpw7f93xn9dtg90z8hukfsy4`
- **Serialized Block Size**: `246 bytes`

Full consensus constants are available in [`genesis/PUBLIC_GENESIS_MANIFEST.json`](genesis/PUBLIC_GENESIS_MANIFEST.json).

---

## 10. Mining & Stratum Mining Setup

### Dual-PoW Mining CLI
QuantyCoin features dual independent Proof-of-Work lanes. Select your target lane via `--lane`:
```bash
# Lane A: SHA-256D ASIC / High-Throughput Mining
python quanty_miner_cli.py --lane sha256d --threads 4 --payout qty1qh46xnlu649ug0yfpw7f93xn9dtg90z8hukfsy4

# Lane B: RFC 7914 Scrypt General-Purpose CPU/GPU Mining
python quanty_miner_cli.py --lane general --threads 4 --payout qty1qh46xnlu649ug0yfpw7f93xn9dtg90z8hukfsy4
```

### Stratum Mining Servers

1. **Stratum V2 Binary Pool Server (Port 3334)**:
   High-efficiency binary framed protocol with dual-lane channel multiplexing:
   ```bash
   python -c "from miner.stratum_v2 import StratumV2Server; s = StratumV2Server(port=3334); s.start(); import time; time.sleep(999999)"
   ```
   - **Connection URL**: `sv2://<ip>:3334`
   - **Features**: Dual-lane channel multiplexing (`pow_lane`), binary framing, low-latency `SetNewPrevHash`.

2. **Stratum V1 Pool Server (Port 3333)**:
   Standard legacy Stratum V1 JSON-RPC protocol:
   ```bash
   python -c "from miner.stratum import StratumServer; s = StratumServer(port=3333); s.start(); import time; time.sleep(999999)"
   ```
   - **Connection URL**: `stratum+tcp://<ip>:3333`


---

## 11. Sovereign Wallet & Desktop Applications

QuantyCoin ships with 5 dedicated Qt6 desktop applications:

1. **Sovereign Full Wallet** (`quanty_wallet_full_app.py`): Native wallet with integrated full node background engine.
2. **Lightning Light Wallet** (`quanty_lightning_wallet_app.py`): Fast client connecting to local or remote node RPC.
3. **Node Manager GUI** (`quanty_node_app.py`): Real-time peer connection table, traffic visualizer, on-chain block explorer, and RPC console.
4. **Standalone Miner GUI** (`quanty_miner_app.py`): Dynamic 60fps hardware-accelerated QPainter hashrate graph, worker thread slider, and Stratum server controller.
5. **Unified Master Suite** (`quanty_suite_app.py`): Master cockpit hosting all subsystems in a single window.

---

## 12. Automated Testing & Independent Verification

Every claim in this repository is directly verifiable using executable commands:

```bash
# 1. Verify zero secret leakage across repository
python scripts/verify_security.py

# 2. Verify genesis block hash, merkle root, and difficulty
python scripts/verify_genesis.py

# 3. Run unit tests (Cryptography, Core, P2P)
python tests/test_crypto.py
python tests/test_core.py
python tests/test_p2p.py

# 4. Run Stratum V1 mining pool integration test
python tests/test_functional_stratum.py

# 5. Run consolidated functional test runner
python tests/test_runner.py

# 6. Run multi-node stress and reorganization hardness matrix
python tests/test_multinode_stress.py
```

Refer to [`VERIFICATION.md`](VERIFICATION.md) for full reproduction logs and cryptographic proofs.

---

## 13. Release Management

Releases follow an evidence-gated verification pipeline requiring zero security alerts, passing test suites, and reproducible binary packages:
- [Release Process Specification](RELEASE_PROCESS.md)
- [Build & Reproducibility Guide](REPRODUCIBILITY.md)
- Native packaging definitions: `packaging/windows/`, `packaging/linux/`, `packaging/macos/`.

---

## 14. Security & Threat Model

- **Security Policy**: [`SECURITY.md`](SECURITY.md) defines supported versions, vulnerability handling, and disclosure SLAs.
- **Threat Model**: [`THREAT_MODEL.md`](THREAT_MODEL.md) documents attack vectors, bounded memory deserialization, and mitigations.
- **Zero Secret Rule**: No private keys, nonces, or vault secrets are ever stored or committed to the repository.
- **Reporting**: Disclose security vulnerabilities confidentially to `timfromhcs@gmail.com`.

---

## 15. Roadmap

Milestone progress is tracked in [`ROADMAP.md`](ROADMAP.md):
- **Phase 1 (Completed)**: Protocol Rebuild, Air-Gapped Genesis, Stratum V1, Multi-Node Hardness.
- **Phase 2 (Active)**: Public Seed Nodes, Compact Block Filters (BIP157/158), Automated Cross-Platform Binaries.
- **Phase 3 (Planned)**: Formal audit of C++ Dilithium integration, Stratum V2 binary framing.

---

## 16. Contributing

Contributions from protocol engineers, cryptographers, and testers are welcomed. Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before submitting pull requests.

---

## 17. Citation & License

```bibtex
@software{QuantyCoin2026,
  author = {Heinrichs, Tim and QuantyCoin Core Contributors},
  title = {QuantyCoin: Independent SHA-256D Proof-of-Work Layer-1 Cryptocurrency},
  url = {https://github.com/timfromhcs/QuantyCoin},
  version = {2.0.0},
  year = {2026}
}
```

Distributed under the terms of the **MIT License**. See [`LICENSE`](LICENSE) and [`COPYING`](COPYING) for details.
