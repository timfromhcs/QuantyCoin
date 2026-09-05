# QuantyCoin Mining & Pool Operator Guide

**Mining Algorithm**: Double-SHA256 (SHA-256D Proof-of-Work)  
**Target Block Interval**: 60 seconds  
**Block Subsidy**: 50 QTY initial (halving every 2,100,000 blocks)  
**Stratum Port**: `3333` (Mainnet), `13333` (Testnet)  

---

## 1. Mining Overview

QuantyCoin uses authoritative SHA-256D Proof-of-Work—the same cryptographic hashing algorithm as Bitcoin. This allows:
- **CPU / GPU Mining**: Suitable for local development, testing, and initial decentralization.
- **ASIC Compatibility**: Standard Bitcoin SHA-256 ASIC mining hardware can connect directly via Stratum V1.
- **Responsive Retargeting**: LWMA-1 adjusts difficulty every single block to prevent hashrate swings.

---

## 2. Solo Mining (Local CPU / GPU)

### Option A: Graphical Miner
Launch the native Qt6 Standalone Miner GUI:
```bash
python quanty_miner_app.py
```
- Enter your payout address (e.g. `qty1q...`).
- Select the number of worker threads (e.g. 4-16 threads).
- Click **Start Mining**. The live QPainter graph displays real-time hashrate (kH/s, MH/s).

### Option B: Command-Line Solo Miner
Run the headless CLI miner against your local full node:
```bash
python quanty_miner_cli.py --threads 4 --payout qty1q...
```

---

## 3. Stratum V1 Mining Pool Setup

QuantyCoin ships with a native Stratum V1 mining pool server built directly into `miner/stratum.py`.

### Starting the Stratum Pool Server
The Stratum server listens by default on TCP port `3333`:
```bash
python -c "
from miner.stratum import StratumServer
server = StratumServer(host='0.0.0.0', port=3333)
server.start()
import time
print('Stratum V1 pool server active on port 3333. Press Ctrl+C to stop.')
while True:
    time.sleep(1)
"
```

### Connecting External Miners
Point your mining client (e.g. CGMiner, BFGMiner, or ASIC controller) to:
- **Stratum URL**: `stratum+tcp://<your-node-ip>:3333`
- **Username**: `your_worker_name` or `<your_qty1q_address>.<worker>`
- **Password**: `x`

### Stratum V1 Wire Protocol Verification
The server handles:
1. `mining.subscribe`: Issues subscription ID, extranonce1, and extranonce2 size.
2. `mining.authorize`: Authenticates worker credentials.
3. `mining.notify`: Pushes new job templates with Merkle roots.
4. `mining.submit`: Validates share work and counts valid shares.

You can verify the Stratum integration test at any time:
```bash
python tests/test_functional_stratum.py
```
