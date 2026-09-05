# QuantyCoin Protocol Specification

**Protocol Version**: QTY3 (`70020`)  
**Network Identifier**: `quantycoin-2.0`  
**Consensus Status**: Frozen  

---

## Authoritative Consensus Parameters

| Parameter | Mainnet Value | Testnet Value | Regtest Value |
| :--- | :--- | :--- | :--- |
| **Protocol Magic** | `0x5155414E` (`QUAN`) | `0x54515541` (`TQUA`) | `0x52515541` (`RQUA`) |
| **P2P Port** | `19888` | `29888` | `39888` |
| **RPC Port** | `19889` | `29889` | `39889` |
| **Stratum V1 Port** | `3333` | `13333` | `23333` |
| **Stratum V2 Port** | `3334` | `13334` | `23334` |
| **Target Block Interval** | `60 seconds` combined | `60 seconds` | `60 seconds` |
| **Mining Lanes** | Lane A (SHA-256D) &bull; Lane B (Scrypt) | Dual-Lane | Dual-Lane |
| **Max Block Size** | `32 MB` (33,554,432 B) | `32 MB` | `32 MB` |
| **Initial Subsidy** | Lane A: 50 QTY &bull; Lane B: 25 QTY | 50 / 25 QTY | 50 / 25 QTY |
| **Halving Schedule** | `2,100,000 blocks` | `2,100,000 blocks` | `2,100,000 blocks` |
| **Max Supply Cap** | `21,000,000 QTY` | `21,000,000 QTY` | `21,000,000 QTY` |
| **Difficulty Algorithm** | **LWMA-1** (window: 45 per lane) | **LWMA-1** | **LWMA-1** |
| **Fork Choice** | **Thermodynamic Chainwork** | Thermodynamic | Thermodynamic |
| **Post-Quantum Cryptography** | **NIST FIPS 204 ML-DSA-44** | ML-DSA-44 | ML-DSA-44 |
| **Coinbase Maturity** | `100 blocks` | `100 blocks` | `100 blocks` |
| **Bech32 / Bech32m HRP** | `qty` (`qty1q`, `qty1p`, `qty1z`) | `tqty` | `rqty` |

---

## Authoritative Specifications

- [QTY3 Protocol Freeze Specification](QTY3_PROTOCOL_FREEZE.md): Ratified constants and immutability invariants.
- [Post-Quantum Cryptography Specification](PQC_SPEC.md): NIST FIPS 204 ML-DSA-44 transaction authorization, Bech32m encodings, and sighash rules.
- [Dual Proof-of-Work Consensus Specification](DUAL_POW_SPEC.md): Lane A SHA-256D ASIC and Lane B RFC 7914 Scrypt mining architecture.
- [Thermodynamic Cumulative Chainwork Specification](CHAINWORK_SPEC.md): Energy-weighted fork-choice defense defeating low-difficulty reorganization attacks.
- [Stratum V2 Binary Protocol Specification](STRATUM_V2_SPEC.md): Binary framing, dual-lane channel multiplexing, and template negotiation.
- [Sovereign UTXO Quantum Migration Specification](MIGRATION_SPEC.md): Automated wallet vulnerability audit and one-click atomic consolidation transactions.
- [Public Genesis Manifest](../../genesis/PUBLIC_GENESIS_MANIFEST.json): Exact JSON manifest of the frozen Genesis block.
- [Public Genesis Summary](../../public_genesis.json): Tokenomics parameters and initial block specifications.
- [Whitepaper Integration Design](WHITEPAPER_INTEGRATION_DESIGN.md): Cryptographic protocol design background.
- [Block Timing Implementation](BLOCK_TIMING_IMPLEMENTATION.md): 60-second block timing, Poisson variance, and propagation mechanics.
