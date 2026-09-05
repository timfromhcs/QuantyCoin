# QuantyCoin Operations & Node Deployment

This section contains operational guides for running full nodes, mining infrastructure, and node maintenance.

---

## Documents

- [Mining Pool Optimization](MINING_POOL_OPTIMIZATION.md): Stratum server configuration, worker allocation, and latency tuning.
- [UTXO Consolidation Guide](UTXO_CONSOLIDATION_OPTIMIZATION.md): Best practices for wallet UTXO maintenance and fee optimization.

---

## Operational Commands

### Running a Full Node
```bash
python quantyd_cli.py
```

### Launching the Standalone Node GUI
```bash
python quanty_node_app.py
```

### Running the Solo Miner
```bash
python quanty_miner_cli.py --threads 4
```

### Running the Native Qt6 Desktop Suite
```bash
python quanty_suite_app.py
```
