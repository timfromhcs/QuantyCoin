# QuantyCoin Protocol Consensus Freeze: QTY2/QTY3 Transition

**Document**: docs/agent/CONSENSUS_FREEZE.md
**Protocol Version**: QTY2 (70020)
**Status**: FROZEN & RATIFIED
**Ratification Date**: 2026-09-05

---

## 1. Consensus Parameter Freeze Ledger

| Parameter | Frozen Value | Enforcement Scope | Invariant Rule |
| :--- | :--- | :--- | :--- |
| **Protocol Version** | 70020 | P2P handshake, block headers | Rejects non-70020 version peers |
| **Network Magic** | 0x5155414e (QUAN) | P2P wire framing | Rejects frames with alien magic bytes |
| **Target Combined Block Time** | 60 seconds | Consensus network cadence | 1 block/min under dual-lane operation |
| **Lane A Target Interval** | 120 seconds | LWMA-1 difficulty window (N=45) | Independent ASIC difficulty adjustment |
| **Lane B Target Interval** | 120 seconds | LWMA-1 difficulty window (N=45) | Independent CPU/GPU difficulty adjustment |
| **Base Block Subsidy** | 50 QTY (5,000,000,000 sat) | Lane A coinbase reward | 100% subsidy for industrial ASIC lane |
| **Lane B Block Subsidy** | 25 QTY (2,500,000,000 sat) | Lane B coinbase reward | 50% subsidy for consumer CPU/GPU lane |
| **Subsidy Halving Window** | 2,100,000 blocks | Supply emission schedule | Halves subsidy every ~4 years |
| **Total Maximum Supply** | <= 21,000,000 QTY | Monetary integrity | Hard supply cap strictly preserved |
| **Lane A PoW Algorithm** | Double SHA-256 (SHA256D) | Lane A block verification | Physical ASIC hardware compatibility |
| **Lane B PoW Algorithm** | RFC 7914 Scrypt (N=1024, r=1, p=1) | Lane B block verification | Memory-hard consumer CPU/GPU PoW |
| **Thermodynamic Weight W_A** | 1 | Cumulative chainwork calculation | Base thermodynamic energy reference |
| **Thermodynamic Weight W_B** | 2048 | Cumulative chainwork calculation | Normalizes 1024-iteration memory work |
| **Fork-Choice Criterion** | Cumulative Thermodynamic Chainwork | Block connection & reorgs | Block count conveys 0 advantage |
| **PQC Algorithm Standard** | NIST FIPS 204 ML-DSA-44 / Dilithium2 | Transaction authorization | Genuine native lattice signatures |
| **PQC Public Key Length** | 1312 bytes | Address derivation & witness | FIPS 204 ML-DSA-44 parameter |
| **PQC Signature Length** | 2420 bytes | Transaction witness verification | Strict length; zero malleation |
| **PQC Seed Length** | 32 bytes | BIP32 HD deterministic keygen | Domain-separated lattice expansion |
| **PQC Witness Prefix** | 0x51 0x20 (Witness v1) | qty1p... Bech32m addresses | Pure ML-DSA output scriptPubKey |
| **Hybrid Witness Prefix** | 0x52 0x20 (Witness v2) | qty1z... Bech32m addresses | Secp256k1 + ML-DSA dual scriptPubKey |
| **PQC Sighash Domain Tag** | QUANTYCOIN_PQC_SIGHASH_V1 | PQC transaction sighash | Domain separation prevents replay |
| **Stratum V2 Port** | 3334 (SV2_DEFAULT_PORT) | High-efficiency binary mining | Native dual-lane channel multiplexing |

---

## 2. Inviolable Consensus Guarantees

1. **Zero Mock Crypto Fallback**: Any node lacking genuine native FIPS 204 acceleration (libqtydilithium) MUST fail closed and refuse validation. Fallback pseudo-cryptography is permanently barred from consensus.
2. **Failover Liveness**: Either mining lane can independently advance the blockchain if the other lane hashrate collapses to zero.
3. **Anti-Grinding Chainwork**: Low-difficulty Lane B blocks cannot reorg an honest chain with higher cumulative energy commitment.
