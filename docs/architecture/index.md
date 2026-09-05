# QuantyCoin Architecture Documentation

This section provides comprehensive technical documentation on the internal structure, component topology, and state machines of QuantyCoin 2.0 (QTY2).

---

## Documents

- [System Architecture Specification](../../ARCHITECTURE.md): Authoritative high-level architectural specification, subsystem breakdowns, and Mermaid component diagrams.
- [Historical C++ & Design Document](doc-qty-design.md): Deep-dive design notes for C++ kernel modules, memory allocation, and protocol abstractions.

---

## Subsystem Overview

| Component | Directory | Description |
| :--- | :--- | :--- |
| **Consensus State Machine** | `core/` | Block headers, SegWit transactions, UTXO set, undo journals, LWMA difficulty, and mempool. |
| **Cryptography** | `crypto/` | Pure Secp256k1 (RFC 6979), Ed25519, BIP39 mnemonic seeds, BIP44 derivation, and Bech32. |
| **P2P Gossip Network** | `network/` | Binary wire framing (`QUAN` / `0x5155414E`), handshake, inventory gossip, and peer management. |
| **Node Daemon & RPC** | `node/` | Chainstate indexer, best-tip tracking, fork resolution, and threaded JSON-RPC 2.0 server. |
| **Mining & Stratum** | `miner/` | Authoritative SHA-256D engine, block template generator, and Stratum V1 TCP server (port 3333). |
| **Wallet** | `wallet/` | Sovereign HD key derivation, transaction builder, and client RPC interface. |
| **Desktop Applications**| `ui/` | Native Qt6 applications for Node, Sovereign Wallet, Miner, and unified Suite. |
