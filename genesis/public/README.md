# QuantyCoin QTY4 Public Genesis Block

**Chain Identifier**: `quantycoin-4.0`  
**Protocol Version**: `70040`  
**Genesis Block Hash**: `000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`  
**Merkle Root**: `3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea`  

---

## Public Consensus Inputs

- **Timestamp String**: `"2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol"`
- **Unix Timestamp**: `1788614400`
- **Target Bits**: `0x1e0fffff`
- **Winning Nonce**: `2951011`
- **Coinbase Payout Address**: `qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf`
- **Coinbase ScriptPubKey**: `0014e144bcff091f7dc11fa8714134e65ab9cc558166`
- **Coinbase Reward**: `50 QTY` (5000000000 satoshis)

---

## Independent Reproducibility & Dual-Path Verification

This Genesis Block is 100% publicly reproducible without accessing any private key or generation secret.
To verify with both Path 1 (Core engine) and Path 2 (Zero-dependency standalone Python):

```bash
python scripts/verify_qty4_genesis_dual_path.py
```

Both independent paths produce identical byte-level serializations, hashes, and Merkle roots.
