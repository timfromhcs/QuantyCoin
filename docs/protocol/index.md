# QuantyCoin Protocol Specification

**Protocol Version**: QTY4 (`70040`)  
**Network Identifier**: `quantycoin-4.0`  
**Consensus Status**: Frozen  

---

## Authoritative Consensus Parameters

| Parameter | Mainnet Value | Testnet Value | Regtest Value |
| :--- | :--- | :--- | :--- |
| **Protocol Magic** | `0x51545934` (`QTY4`) | `0x54515434` (`TQT4`) | `0x52515434` (`RQT4`) |
| **P2P Port** | `19444` | `29444` | `39444` |
| **RPC Port** | `19445` | `29445` | `39445` |
| **Stratum V1 Port** | `3333` | `13333` | `23333` |
| **Stratum V2 Port** | `3334` | `13334` | `23334` |
| **Target Block Interval** | `60 seconds` combined | `60 seconds` | `60 seconds` |
| **Mining Lanes** | Lane A (SHA-256D) &bull; Lane B (Scrypt) | Dual-Lane | Dual-Lane |
| **Max Block Size** | `32 MB` (33,554,432 B) | `32 MB` | `32 MB` |
| **Initial Subsidy** | Lane A: 50 QTY &bull; Lane B: 25 QTY | 50 / 25 QTY | 50 / 25 QTY |
| **Halving Schedule** | `2,100,000 blocks` (bitwise shift) | `2,100,000 blocks` | `2,100,000 blocks` |
| **Max Supply Cap** | `21,000,000 QTY` (`Amount`) | `21,000,000 QTY` | `21,000,000 QTY` |
| **Difficulty Algorithm** | **LWMA-1** (window: 45 per lane) | **LWMA-1** | **LWMA-1** |
| **Fork Choice** | **Weighted Cumulative Work** | Cumulative Work | Cumulative Work |
| **Post-Quantum Cryptography** | **NIST FIPS 204 ML-DSA-44** | ML-DSA-44 | ML-DSA-44 |
| **Coinbase Maturity** | `100 blocks` | `100 blocks` | `100 blocks` |
| **Bech32 / Bech32m HRP** | `qty` (`qty1q`, `qty1p`, `qty1z`) | `tqty` | `rqty` |

---

## Authoritative Specifications

- [QTY4 Master Protocol Specification](QTY4_SPEC.md): Canonical protocol architecture, state transitions, and parameters.
- [Consensus Rules & Invariant Proofs](CONSENSUS_RULES.md): Formal mathematical and structural consensus rules.
- [Proof-of-Work Specification](POW_SPEC.md): Lane A SHA-256D ASIC and Lane B RFC 7914 Scrypt mining architecture.
- [Difficulty Adjustment Specification](DIFFICULTY_SPEC.md): LWMA-1 45-block window retargeting mechanics.
- [Weighted Chainwork Specification](CHAINWORK_SPEC.md): Weighted Cumulative Work ($W_A=1, W_B=2048$) fork choice.
- [Post-Quantum Cryptography Specification](PQC_SPEC.md): NIST FIPS 204 ML-DSA-44 transaction authorization and sighash rules.
- [Address Encoding Specification](ADDRESS_SPEC.md): Native Bech32, Bech32m ML-DSA, and Hybrid witness formats.
- [Binary Serialization Specification](SERIALIZATION_SPEC.md): Canonical wire and storage encoding.
- [P2P Network Protocol Specification](NETWORK_SPEC.md): Framing, handshakes, inventory relay, and peer discovery.
- [Genesis Block Specification](GENESIS_SPEC.md): Public parameters, coinbases, and dual-path reproducibility.
- [Public Genesis Manifest](../../genesis/PUBLIC_GENESIS_MANIFEST.json): Exact JSON manifest of the frozen Genesis block.
