# QuantyCoin 2.0 (QTY2) Architectural Decisions & Protocol Freeze Records

All immutable protocol parameters and key architectural choices are recorded here.

---

## 1. Protocol Architecture Overview

- **Protocol Version**: `QTY2` (`70020`)
- **Proof-of-Work**: SHA-256D (Double SHA-256)
- **Difficulty Adjustment Algorithm**: LWMA-1 (Linear-Weighted Moving Average, window: 45 blocks, bounded oscillation clamping)
- **Target Block Interval**: 60 seconds (1 minute)
- **Genesis Block Reward**: 50 QTY (5,000,000,000 satoshis)
- **Subsidy Halving Interval**: 2,100,000 blocks (~4 years)
- **Maximum Supply**: 21,000,000 QTY (2,100,000,000,000,000 satoshis)
- **Maximum Block Size**: 32 MB (33,554,432 bytes)
- **Coinbase Maturity**: 100 blocks
- **Smallest Unit**: 1 Satoshi (1 QTY = 100,000,000 Satoshis)
- **Network Magic Bytes**:
  - Mainnet: `0x5155414e` (`QUAN`)
  - Testnet: `0x54515541` (`TQUA`)
  - Regtest: `0x52515541` (`RQUA`)
- **Default Ports**:
  - Mainnet: P2P `19888`, RPC `19889`, Stratum `3333`
  - Testnet: P2P `29888`, RPC `29889`, Stratum `13333`
  - Regtest: P2P `39888`, RPC `39889`, Stratum `23333`
- **Address Encodings**:
  - Native Bech32 Prefix: `qty` (Mainnet), `tqty` (Testnet), `rqty` (Regtest)
  - Legacy Base58 P2PKH Prefix: `0x3a` (Starts with 'Q')
  - Legacy Base58 P2SH Prefix: `0x44` (Starts with 'T')
  - BIP32 HD Extended Public Key: `qpub` (`0x0488B21E`), Private: `qprv` (`0x0488ADE4`)
  - URI Scheme: `quantycoin:`
- **Post-Quantum Cryptography Architecture**:
  - Modular crypto provider with dual-layer signature support:
    - Layer 1 ECDSA secp256k1 for high-throughput micro-transactions / backward compatibility
    - Post-quantum signature abstraction (Dilithium3 / ML-DSA hybrid) for quantum-resistant vaults and high-value UTXOs
