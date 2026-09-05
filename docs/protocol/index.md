# QuantyCoin Protocol Specification

**Protocol Version**: QTY2 (`70020`)  
**Network Identifier**: `quantycoin-2.0`  
**Consensus Status**: Frozen  

---

## Authoritative Consensus Parameters

| Parameter | Mainnet Value | Testnet Value | Regtest Value |
| :--- | :--- | :--- | :--- |
| **Protocol Magic** | `0x5155414E` (`QUAN`) | `0x54515541` (`TQUA`) | `0x52515541` (`RQUA`) |
| **P2P Port** | `19888` | `29888` | `39888` |
| **RPC Port** | `19889` | `29889` | `39889` |
| **Stratum Port** | `3333` | `13333` | `23333` |
| **Target Block Interval** | `60 seconds` | `60 seconds` | `60 seconds` |
| **Max Block Size** | `32 MB` (33,554,432 B) | `32 MB` | `32 MB` |
| **Initial Subsidy** | `50 QTY` | `50 QTY` | `50 QTY` |
| **Halving Schedule** | `2,100,000 blocks` | `2,100,000 blocks` | `2,100,000 blocks` |
| **Max Supply Cap** | `21,000,000 QTY` | `21,000,000 QTY` | `21,000,000 QTY` |
| **Difficulty Algorithm** | **LWMA-1** (window: 45) | **LWMA-1** | **LWMA-1** |
| **Coinbase Maturity** | `100 blocks` | `100 blocks` | `100 blocks` |
| **Bech32 HRP** | `qty` | `tqty` | `rqty` |

---

## Documents

- [Public Genesis Manifest](../../genesis/PUBLIC_GENESIS_MANIFEST.json): Exact JSON manifest of the frozen Genesis block.
- [Public Genesis Summary](../../public_genesis.json): Tokenomics parameters and initial block specifications.
- [Whitepaper Integration Design](WHITEPAPER_INTEGRATION_DESIGN.md): Cryptographic protocol design background.
- [Block Timing Implementation](BLOCK_TIMING_IMPLEMENTATION.md): 60-second block timing, Poisson variance, and propagation mechanics.
