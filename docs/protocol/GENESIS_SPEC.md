# QuantyCoin QTY4 Genesis Block Specification

**Chain ID**: `quantycoin-4.0`  
**Protocol Version**: `70040`  
**Genesis Hash**: `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`  
**Merkle Root**: `3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea`  

---

## 1. Public Genesis Parameters

| Parameter | Value |
| :--- | :--- |
| **Timestamp String** | `"2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol"` |
| **Unix Epoch Timestamp** | `1788614400` (2026-09-05 16:00:00 UTC) |
| **Target Bits** | `0x1e0fffff` (Standard easy test PoW limit) |
| **Winning Nonce** | `2951011` |
| **Coinbase Value** | `50 QTY` (`5,000,000,000` satoshis) |
| **Coinbase Payout Address** | `qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf` |
| **Coinbase ScriptPubKey** | `0014e144bcff091f7dc11fa8714134e65ab9cc558166` |

---

## 2. Payout Address Derivation

The Genesis payout address is deterministically derived from a public community commitment with zero private keys:

$$\text{Seed} = \text{"QUANTYCOIN\_QTY4\_SOVEREIGN\_GENESIS\_COMMUNITY\_2026"}$$
$$\text{WitnessProgram} = \text{RIPEMD160}(\text{SHA256}(\text{Seed}))$$
$$\text{Address} = \text{Bech32}(\text{"qty"}, 0, \text{WitnessProgram})$$

Because no entity holds the private key for $\text{WitnessProgram}$, the genesis reward is provably locked/burned, guaranteeing zero premine and an uncompromised fair launch.

---

## 3. Dual-Path Verification Protocol

Verification can be executed via:
```bash
python scripts/verify_qty4_genesis_dual_path.py
```
This script executes two separate verification engines:
- **Path 1**: QuantyCoin core library (`core/block.py`, `core/transaction.py`).
- **Path 2**: Pure zero-dependency standalone implementation using only Python standard library `struct` and `hashlib`.

Both paths yield 100% byte-for-byte identical block serializations, header hexes, Merkle roots, and block hashes.
