# QuantyCoin Developer & Architecture Onboarding Guide

This guide is designed for systems engineers, protocol researchers, and contributors looking to understand, build, and test QuantyCoin 2.0 (QTY2).

---

## 1. Codebase Organization

```
QuantyCoin/
├── core/             # Consensus state machine, UTXO set, Mempool, Block & Tx models
├── crypto/           # Pure Secp256k1 (RFC 6979), Ed25519, BIP39/44 HD keys, Hashes
├── network/          # TCP binary wire framing, P2P peer manager, PEX gossip
├── node/             # Full Node daemon (quantyd), Chainstate indexer, JSON-RPC 2.0
├── wallet/           # HD Wallet key derivation, coin selection, transaction signer
├── miner/            # SHA-256D engine, block templates, Stratum V1 pool server
├── ui/               # Native Qt6 Cyberpunk Desktop applications
├── tests/            # Automated test framework, functional tests, stress matrix
├── genesis/          # PUBLIC_GENESIS_MANIFEST.json and consensus freeze parameters
├── docs/             # Technical documentation architecture
└── packaging/        # NSIS, InnoSetup, Debian deb, AppImage, and DMG packaging
```

---

## 2. Environment Setup

### Requirements
- Python 3.10, 3.11, 3.12, or 3.13
- Optional (for Qt6 desktop applications): `pip install PySide6 qrcode pillow`
- Optional (for test runner): `pip install pytest`

### Clone & Verify
```bash
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin

# Run zero-leak security check
python scripts/verify_security.py
```

---

## 3. Where Consensus Lives

All authoritative consensus rules live in `core/`:
- **`core/block.py`**:
  - `BlockHeader.serialize()`: Canonical 80-byte header format.
  - `BlockHeader.verify_pow()`: Validates double-SHA256 hash against compact target bits.
  - `Block.verify_merkle_root()`: Validates transaction tree root.
- **`core/transaction.py`**:
  - `Transaction.serialize()`: Strict BIP141 witness serialization.
  - `Transaction.sign_input()`: RFC 6979 deterministic ECDSA signing.
- **`core/consensus.py`**:
  - `calculate_next_work_required_lwma()`: 45-block single-block difficulty retargeting.
  - `get_block_subsidy()`: 50 QTY halving schedule every 2,100,000 blocks.
- **`core/genesis_constants.py`**:
  - Authoritative frozen consensus constants (`GENESIS_HASH`, `MAGIC_BYTES`, `TARGET_BLOCK_TIME`).

---

## 4. Running the Test Suite

QuantyCoin includes a multi-tiered automated test suite:

### A. Unit Tests (Crypto & Core)
```bash
python tests/test_crypto.py
python tests/test_core.py
python tests/test_p2p.py
```

### B. Functional Integration Tests
```bash
python tests/test_functional_stratum.py
python tests/test_runner.py
```

### C. Multi-Node Stress & Chaos Matrix
Spins up multi-node local networks, tests mempool burst ingestion (500 TXs), simulates 10-block deep chain reorganizations, enforces double-spend rejection, and verifies socket drop recovery:
```bash
python tests/test_multinode_stress.py
```

---

## 5. Running a Local Multi-Node Regtest Network

You can orchestrate a multi-node network programmatically using `tests/test_framework.py`:

```python
from tests.test_framework import QuantyTestFramework

class MyClusterTest(QuantyTestFramework):
    def __init__(self):
        super().__init__(num_nodes=3, base_p2p_port=21500, base_rpc_port=22500)

    def run_test(self):
        print(f"Node 0 height: {self.nodes[0].rpc.get_block_count()}")
        self.generate(0, 5)
        self.sync_blocks()
        print(f"Node 1 height after sync: {self.nodes[1].rpc.get_block_count()}")

if __name__ == "__main__":
    MyClusterTest().main()
```
