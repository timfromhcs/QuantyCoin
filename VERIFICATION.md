# QuantyCoin Independent Verification Guide

**Goal**: Enable any developer, auditor, or node operator to independently verify all cryptographic proofs, consensus rules, and integration tests from a fresh clone.

---

## 1. Quick Verification (< 3 Minutes)

```bash
# 1. Verify that no private secrets or credentials exist in the tree
python scripts/verify_security.py

# 2. Verify cryptography (BIP39, BIP44, Secp256k1, Bech32)
python tests/test_crypto.py

# 3. Verify core transaction serialization, Merkle root & LWMA difficulty
python tests/test_core.py

# 4. Verify binary P2P framing and wire serialization
python tests/test_p2p.py

# 5. Verify Stratum V1 mining pool protocol
python tests/test_functional_stratum.py

# 6. Execute full multi-node test runner
python tests/test_runner.py

# 7. Execute multi-node stress and hardness matrix
python tests/test_multinode_stress.py
```

---

## 2. Verifying the Genesis Block

The Genesis block is fully deterministic and independently verifiable:

```bash
python -c "
import json
from core.genesis_constants import GENESIS_HASH, GENESIS_MERKLE_ROOT, GENESIS_NONCE, GENESIS_BITS
with open('genesis/PUBLIC_GENESIS_MANIFEST.json') as f:
    m = json.load(f)
assert m['genesis_hash'] == GENESIS_HASH, 'Genesis hash mismatch!'
assert m['merkle_root'] == GENESIS_MERKLE_ROOT, 'Merkle root mismatch!'
assert m['nonce'] == GENESIS_NONCE, 'Nonce mismatch!'
assert m['bits'] == GENESIS_BITS, 'Bits mismatch!'
print('[VERIFIED] Genesis manifest matches core consensus constants exactly.')
"
```

---

## 3. Verifying Node Consensus Startup

Run a standalone verification script that spins up an isolated `Chainstate` instance:

```bash
python -c "
from node.chainstate import Chainstate
cs = Chainstate()
print(f'Node initialized successfully. Tip Hash: {cs.best_hash_hex}, Height: {cs.best_height}')
"
```

Expected output:
```
Node initialized successfully. Tip Hash: 00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba, Height: 0
```

---

## 4. Test Suite Pass Criteria

| Checkpoint | Target | Verified Output |
| :--- | :--- | :--- |
| **`test_crypto.py`** | Crypto Pipeline | `100% PASS` |
| **`test_core.py`** | Serialization & Consensus | `100% PASS` |
| **`test_p2p.py`** | Framing & Wire | `100% PASS` |
| **`test_functional_stratum.py`** | Stratum V1 Pool Engine | `100% PASS` |
| **`test_functional_mining.py`** | Mining & Subsidy | `100% PASS` |
| **`test_functional_wallet.py`** | HD Wallet & Tx Relay | `100% PASS` |
| **`test_functional_p2p.py`** | Multi-Node Relay | `100% PASS` |
| **`test_functional_reorg.py`** | Deep 10-Block Reorg | `100% PASS` |
| **`test_multinode_stress.py`** | 500-TX Saturation & Chaos | `100% PASS` |
| **`test_runner.py`** | Consolidated Suite | `100% PASS (0 Failures)` |
