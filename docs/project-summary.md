# QuantyCoin 3.0 (QTY3) Project Summary

**Canonical Name**: QuantyCoin  
**Symbol**: QTY  
**Protocol Version**: QTY3 (`70020`)  
**Software Version**: `3.0.0`  
**License**: MIT License  
**Repository**: `https://github.com/timfromhcs/QuantyCoin`  

---

## 1. Executive Summary

QuantyCoin is an open-source, independently identified Layer-1 cryptocurrency combining asymmetric Dual Proof-of-Work mining (Lane A SHA-256D ASIC & Lane B RFC 7914 Scrypt CPU/GPU), NIST FIPS 204 ML-DSA-44 post-quantum transaction authorization, cumulative thermodynamic chainwork, rapid 60-second combined block intervals, responsive LWMA-1 difficulty adjustment, 32 MB block capacity, native Stratum V2 binary framing and V1 pool architecture, BIP39/44 HD wallets with Bech32/Bech32m witness encodings (`qty1q...`, `qty1p...`, `qty1z...`), and a binary P2P gossip protocol (`QUAN` / `0x5155414E`).

---

## 2. Technical Consensus Specifications

- **Hashing Algorithms**: Asymmetric Dual-PoW:
  - Lane A: Double-SHA256 (SHA-256D ASIC)
  - Lane B: RFC 7914 Scrypt 1024/1/1 (General-Purpose CPU/GPU)
- **Genesis Block Hash**: `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`
- **Genesis Merkle Root**: `ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f`
- **Genesis Timestamp**: `1788600000` (Epoch fixed)
- **Difficulty Retargeting**: LWMA-1 (Linear-Weighted Moving Average across 45-block per-lane window)
- **Fork-Choice Rule**: Cumulative Thermodynamic Chainwork ($W_A=1, W_B=2048$)
- **Target Block Time**: 60 seconds combined (120 seconds per lane)
- **Maximum Block Size**: 32 MB (33,554,432 bytes)
- **Initial Subsidy**: Lane A: 50.00 QTY &bull; Lane B: 25.00 QTY
- **Halving Interval**: Every 2,100,000 blocks (~4 years)
- **Maximum Supply Hard Cap**: 21,000,000 QTY ($2.1 \times 10^{15}$ Satoshis)
- **Smallest Unit**: 1 Satoshi ($10^{-8}$ QTY)
- **Coinbase Maturity**: 100 confirmations
- **Post-Quantum Cryptography**: NIST FIPS 204 ML-DSA-44 native C lattice acceleration (`libqtydilithium`)
- **Default Ports**:
  - Mainnet: P2P `19888`, RPC `19889`, Stratum V1 `3333`, Stratum V2 `3334`
  - Testnet: P2P `29888`, RPC `29889`, Stratum V1 `13333`, Stratum V2 `13334`
  - Regtest: P2P `39888`, RPC `39889`, Stratum V1 `23333`, Stratum V2 `23334`
- **Address Prefixes**:
  - Native Witness Bech32 (Witness v0): `qty1q...`
  - Native Post-Quantum Bech32m (Witness v1): `qty1p...`
  - Hybrid Defense-in-Depth Bech32m (Witness v2): `qty1z...`
  - Legacy P2PKH Base58Check: `0x3a` (Starts with 'Q')

---

## 3. Implementation Status Classification

| Capability | Status | Notes |
| :--- | :--- | :--- |
| **Dual-PoW Mining (SHA-256D & Scrypt)** | **VERIFIED** | 100% test pass; independent per-lane block production verified. |
| **Thermodynamic Chainwork** | **VERIFIED** | Mathematical work weights ($W_A=1, W_B=2048$) defeat low-diff reorganizations. |
| **NIST FIPS 204 ML-DSA-44 PQC** | **VERIFIED** | Native C lattice acceleration; fail-closed consensus; zero pseudo-crypto. |
| **Stratum V2 Binary Protocol** | **VERIFIED** | TCP port 3334; 6-byte binary framing; dual-lane channel multiplexing. |
| **Legacy UTXO Quantum Migration** | **VERIFIED** | Automated audit and one-click atomic consolidation transactions in wallet. |
| **Air-Gapped Genesis** | **VERIFIED** | Independently reproduced from public parameters with runtime assertions. |
| **P2P Wire Network** | **VERIFIED** | Framing, handshake, inventory relay across multi-node clusters. |
| **Stratum V1 Server** | **VERIFIED** | TCP port 3333; ASIC share validation, difficulty retargeting. |
| **BIP39/44 Multi-Mode HD Wallet** | **VERIFIED** | Derives classical, pure post-quantum, and hybrid addresses. |
| **Threaded JSON-RPC** | **VERIFIED** | Standard node, mining lanes, chainwork, and wallet RPC endpoints. |
| **Qt6 Desktop Suite** | **VERIFIED** | Full Node GUI, Sovereign Wallet, Miner, and Master Suite on Windows & Linux. |

---

## 4. Verification Resources

- Public Genesis Manifest: `genesis/PUBLIC_GENESIS_MANIFEST.json`
- Verification Guide: `VERIFICATION.md`
- Threat Model: `THREAT_MODEL.md`
- Security Disclosures: `SECURITY.md`
- Protocol Freeze Specification: `docs/protocol/QTY3_PROTOCOL_FREEZE.md`
