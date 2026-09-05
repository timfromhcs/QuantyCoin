# QuantyCoin QTY4 P2P & Mining Network Specification

**Protocol**: QTY4 (70040)  
**Wire Magic**: `0x51545934` (`QTY4`)  

---

## 1. Port Assignments

| Network | P2P Gossip | JSON-RPC | Stratum V1 | Stratum V2 |
| :--- | :--- | :--- | :--- | :--- |
| **Mainnet** | `19444` | `19445` | `3333` | `3334` |
| **Testnet** | `29444` | `29445` | `13333` | `13334` |
| **Regtest** | `39444` | `39445` | `23333` | `23334` |

---

## 2. P2P Connection & Handshake Flow

1. **Version Exchange**: Initiator sends `version` message containing protocol version (`70040`), services bitmask, timestamp, and peer address.
2. **Version Acceptance**: Receiver validates version $\ge 70040$ and responds with `verack` followed by its own `version`.
3. **Inventory Relay**: Nodes advertise verified blocks and mempool transactions via `inv` messages.
4. **Header Sync**: Initial block download (IBD) uses `getheaders` to perform headers-first synchronization before retrieving block payloads with `getdata`.

---

## 3. Stratum Protocols

### Stratum V1 (Port 3333)
JSON-RPC line-delimited protocol providing `mining.subscribe`, `mining.authorize`, `mining.notify`, and `mining.submit`.

### Stratum V2 (Port 3334)
Binary framed mining protocol featuring:
- Low-latency wire framing with 6-byte message headers (`extension_type`, `msg_type`, `msg_length`).
- Native dual-lane multiplexing (Lane A SHA-256D and Lane B Scrypt 1024 jobs on separate channel IDs).
- Work distribution reducing bandwidth and stale share rate.
