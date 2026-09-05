# QuantyCoin 4.0 (QTY4) Project Summary

**Canonical Name**: QuantyCoin  
**Symbol**: QTY  
**Protocol Version**: QTY4 (`70040`)  
**Software Version**: `4.0.0`  
**License**: MIT License  
**Repository**: `https://github.com/timfromhcs/QuantyCoin`  

---

## 1. Executive Summary

QuantyCoin is an open-source, independently identified Layer-1 cryptocurrency combining asymmetric Dual Proof-of-Work mining (Lane A SHA-256D ASIC & Lane B RFC 7914 Scrypt CPU/GPU), NIST FIPS 204 ML-DSA-44 post-quantum transaction authorization, cumulative thermodynamic chainwork, rapid 60-second combined block intervals, responsive LWMA-1 difficulty adjustment, pure 64-bit integer monetary arithmetic (`core.money.Amount`), 32 MB block capacity, native Stratum V2 binary framing and V1 pool architecture, BIP39/44 HD wallets with Bech32/Bech32m witness encodings (`qty1q...`, `qty1p...`, `qty1z...`), and a binary P2P gossip protocol (`QTY4` / `0x51545934`).

---

## 2. Technical Consensus Specifications

- **Hashing Algorithms**: Asymmetric Dual-PoW:
  - Lane A: Double-SHA256 (SHA-256D ASIC)
  - Lane B: RFC 7914 Scrypt 1024/1/1 (General-Purpose CPU/GPU)
- **Genesis Block Hash**: `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`
- **Genesis Merkle Root**: `3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea`
- **Genesis Timestamp**: `1788614400`
- **Difficulty Retargeting**: LWMA-1 (Linear-Weighted Moving Average across 45-block per-lane window)
- **Fork-Choice Rule**: Cumulative Thermodynamic Chainwork ($W_A=1, W_B=2048$)
- **Target Block Time**: 60 seconds combined (120 seconds per lane)
- **Maximum Block Size**: 32 MB (33,554,432 bytes)
- **Initial Subsidy**: Lane A: 50.00 QTY &bull; Lane B: 25.00 QTY
- **Halving Interval**: Every 2,100,000 blocks (~4 years) via bitwise integer right-shift
- **Maximum Supply Hard Cap**: 21,000,000 QTY ($2.1 \times 10^{15}$ Satoshis via `Amount`)
- **Smallest Unit**: 1 Satoshi ($10^{-8}$ QTY)
- **Coinbase Maturity**: 100 confirmations
- **Post-Quantum Cryptography**: NIST FIPS 204 ML-DSA-44 native C lattice acceleration (`libqtydilithium`)
- **Default Ports**:
  - Mainnet: P2P `19444`, RPC `19445`, Stratum V1 `3333`, Stratum V2 `3334`
  - Testnet: P2P `29444`, RPC `29445`, Stratum V1 `13333`, Stratum V2 `13334`
  - Regtest: P2P `39444`, RPC `39445`, Stratum V1 `23333`, Stratum V2 `23334`
- **Address Prefixes**:
  - Native Witness Bech32 (Witness v0): `qty1q...`
  - Native Post-Quantum Bech32m (Witness v1): `qty1p...`
  - Hybrid Defense-in-Depth Bech32m (Witness v2): `qty1z...`
  - Legacy P2PKH Base58Check: `0x3a` (Starts with 'Q')

---

## 3. Implementation Status Classification

| Capability | Status | Notes |
| :--- | :--- | :--- |
| **Pure Integer Consensus** | **VERIFIED** | 64-bit checked arithmetic (`core.money.Amount`), zero float arithmetic. |
| **Dual-PoW Mining (SHA-256D & Scrypt)** | **VERIFIED** | 100% test pass; independent per-lane block production verified. |
| **Thermodynamic Chainwork** | **VERIFIED** | Mathematical work weights ($W_A=1, W_B=2048$) defeat low-diff reorganizations. |
| **NIST FIPS 204 ML-DSA-44 PQC** | **VERIFIED** | Native C lattice acceleration; fail-closed consensus; zero pseudo-crypto. |
| **Stratum V2 Binary Protocol** | **VERIFIED** | TCP port 3334; 6-byte binary framing; dual-lane channel multiplexing. |
| **Legacy UTXO Quantum Migration** | **VERIFIED** | Automated audit and one-click atomic consolidation transactions in wallet. |
| **Public Deterministic Genesis** | **VERIFIED** | Independently reproduced from public parameters with dual-path byte-for-byte identity. |
| **P2P Wire Network** | **VERIFIED** | Framing with magic `0x51545934`, handshake, inventory relay on port 19444. |
| **Stratum V1 Server** | **VERIFIED** | TCP port 3333; ASIC share validation, difficulty retargeting. |
| **BIP39/44 Multi-Mode HD Wallet** | **VERIFIED** | Derives classical, pure post-quantum, and hybrid addresses. |
| **Threaded JSON-RPC** | **VERIFIED** | Standard node, mining lanes, chainwork, and wallet RPC endpoints on port 19445. |
| **Qt6 Desktop Suite** | **VERIFIED** | Full Node GUI, Sovereign Wallet, Miner, and Master Suite on Windows & Linux. |

---

## 4. Verification Resources

- Public Genesis Manifest: `genesis/PUBLIC_GENESIS_MANIFEST.json`
- Verification Guide: `VERIFICATION.md`
- Threat Model: `THREAT_MODEL.md`
- Security Disclosures: `SECURITY.md`
- QTY4 Protocol Specification: `docs/protocol/QTY4_SPEC.md`
- Protocol Status & Readiness: `docs/STATUS.md`
