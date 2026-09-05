# QuantyCoin 2.0 (QTY2) Project Summary

**Canonical Name**: QuantyCoin  
**Symbol**: QTY  
**Protocol Version**: QTY2 (`70020`)  
**Software Version**: `2.0.0`  
**License**: MIT License  
**Repository**: `https://github.com/timfromhcs/QuantyCoin`  

---

## 1. Executive Summary

QuantyCoin is an open-source, independently identified Layer-1 cryptocurrency combining double-SHA256 (SHA-256D) Proof-of-Work mining, rapid 60-second block intervals, responsive LWMA-1 difficulty adjustment, 32 MB block capacity, native Stratum V1 mining pool architecture, BIP39/44 HD wallets with Bech32 native witness encoding (`qty1q...`), and a binary P2P gossip protocol (`QUAN` / `0x5155414E`).

---

## 2. Technical Consensus Specifications

- **Hashing Algorithm**: Double-SHA256 (SHA-256D Proof-of-Work)
- **Genesis Block Hash**: `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`
- **Genesis Merkle Root**: `ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f`
- **Genesis Timestamp**: `1788600000` (Epoch fixed)
- **Difficulty Retargeting**: LWMA-1 (Linear-Weighted Moving Average across 45-block window)
- **Target Block Time**: 60 seconds (1 minute)
- **Maximum Block Size**: 32 MB (33,554,432 bytes)
- **Initial Subsidy**: 50.00 QTY ($5 \times 10^9$ Satoshis)
- **Halving Interval**: Every 2,100,000 blocks (~4 years)
- **Maximum Supply Hard Cap**: 21,000,000 QTY ($2.1 \times 10^{15}$ Satoshis)
- **Smallest Unit**: 1 Satoshi ($10^{-8}$ QTY)
- **Coinbase Maturity**: 100 confirmations
- **Default Ports**:
  - Mainnet: P2P `19888`, RPC `19889`, Stratum `3333`
  - Testnet: P2P `29888`, RPC `29889`, Stratum `13333`
  - Regtest: P2P `39888`, RPC `39889`, Stratum `23333`
- **Address Prefix**:
  - Native Witness Bech32: `qty` (e.g. `qty1q...`)
  - Legacy P2PKH Base58Check: `0x3a` (Starts with 'Q')

---

## 3. Implementation Status Classification

| Capability | Status | Notes |
| :--- | :--- | :--- |
| **SHA-256D Consensus** | **VERIFIED** | 100% test pass; runtime assertion active. |
| **Air-Gapped Genesis** | **VERIFIED** | Independently reproduced from public parameters. |
| **P2P Wire Network** | **VERIFIED** | Framing, handshake, inventory relay across 3-node clusters. |
| **Stratum V1 Server** | **VERIFIED** | TCP port 3333; share validation, difficulty retargeting. |
| **BIP39/44 HD Wallet** | **VERIFIED** | 24-word seed generation, RFC 6979 ECDSA transaction signing. |
| **Threaded JSON-RPC** | **VERIFIED** | Standard node, mining, and wallet RPC methods operational. |
| **Qt6 Desktop Suite** | **IMPLEMENTED** | Node GUI, Sovereign Wallet, Miner, and Master Suite. |
| **Dilithium PQ C++** | **EXPERIMENTAL**| Vendored reference in `src/`; audit remediations underway. |
| **Stratum V2** | **PLANNED** | Extension hooks preserved; V1 is authoritative production target. |

---

## 4. Verification Resources

- Public Genesis Manifest: `genesis/PUBLIC_GENESIS_MANIFEST.json`
- Verification Guide: `VERIFICATION.md`
- Threat Model: `THREAT_MODEL.md`
- Security Disclosures: `SECURITY.md`
