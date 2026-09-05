# QuantyCoin Architecture Documentation

This section provides comprehensive technical documentation on the internal structure, component topology, and state machines of QuantyCoin 3.0 (QTY3).

---

## Documents

- [System Architecture Specification](../../ARCHITECTURE.md): Authoritative high-level architectural specification, subsystem breakdowns, and Mermaid component diagrams.
- [Historical C++ & Design Document](doc-qty-design.md): Deep-dive design notes for C++ kernel modules, memory allocation, and protocol abstractions.

---

## Subsystem Overview

| Component | Directory | Description |
| :--- | :--- | :--- |
| **Consensus State Machine** | `core/` | Block headers, dual-PoW lanes (SHA-256D & Scrypt), SegWit transactions, UTXO set, undo journals, LWMA-1 difficulty, and mempool. |
| **Cryptography** | `crypto/` | NIST FIPS 204 ML-DSA-44 post-quantum lattice signatures, Secp256k1 (RFC 6979), Ed25519, BIP39/44 HD derivation, and Bech32/Bech32m. |
| **P2P Gossip Network** | `network/` | Binary wire framing (`QUAN` / `0x5155414E`), handshake, inventory gossip, and peer management. |
| **Node Daemon & RPC** | `node/` | Thermodynamic chainwork tracking, best-tip selection, fork resolution, and threaded JSON-RPC 2.0 server. |
| **Mining & Stratum** | `miner/` | Dual-lane mining engine (SHA-256D & Scrypt), block template generator, Stratum V1 (port 3333) and Stratum V2 (port 3334) servers. |
| **Wallet** | `wallet/` | Sovereign HD key derivation, PQC & hybrid transaction builder, UTXO quantum migration assistant, and client RPC interface. |
| **Desktop Applications**| `ui/` | Native Qt6 applications for Node, Sovereign Wallet, Miner, and unified Suite. |
