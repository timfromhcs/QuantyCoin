# QuantyCoin Independent Verification Guide

**Goal**: Enable any developer, auditor, or node operator to independently verify all cryptographic proofs, consensus rules, and integration tests from a fresh clone.  
**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  

---

## 1. Quick Verification (< 3 Minutes)

```bash
# 1. Verify that no private secrets or credentials exist in the tree
python scripts/verify_security.py

# 2. Verify dual-path independent genesis block reproduction
python scripts/verify_qty4_genesis_dual_path.py

# 3. Verify cryptography (BIP39, BIP44, Secp256k1, Bech32, ML-DSA-44)
python tests/test_crypto.py

# 4. Verify core money integer arithmetic, consensus & LWMA difficulty
python tests/test_core.py

# 5. Verify PQC, Dual-PoW, and Stratum V2 binary framing
python tests/test_pqc_dualpow_sv2.py

# 6. Verify adversarial robustness & hostile input rejection
python tests/test_adversarial_qty4.py

# 7. Execute consolidated test runner
python tests/test_runner.py

# 8. Execute multi-node stress and hardness matrix
python tests/test_multinode_stress.py
```

---

## 2. Verifying the Genesis Block

The Genesis block is fully deterministic, 100% public, and independently verifiable:

```bash
python -c "
import json
from core.genesis_constants import GENESIS_HASH, GENESIS_MERKLE_ROOT, GENESIS_NONCE, GENESIS_BITS
with open('genesis/public/genesis_parameters.json') as f:
    m = json.load(f)
assert m['genesis_hash'] == GENESIS_HASH, 'Genesis hash mismatch!'
assert m['merkle_root'] == GENESIS_MERKLE_ROOT, 'Merkle root mismatch!'
assert m['nonce'] == GENESIS_NONCE, 'Nonce mismatch!'
assert m['bits'] == GENESIS_BITS, 'Bits mismatch!'
print('[VERIFIED] Genesis manifest matches core consensus constants exactly.')
"
```

Expected output:
```
[VERIFIED] Genesis manifest matches core consensus constants exactly.
```

---

## 3. Verifying Node Consensus Startup

Run a standalone verification snippet that spins up an isolated `Chainstate` instance:

```bash
python -c "
from node.chainstate import Chainstate
cs = Chainstate()
print(f'Node initialized successfully. Tip Hash: {cs.best_hash_hex}, Height: {cs.best_height}')
"
```

Expected output:
```
Node initialized successfully. Tip Hash: 000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3, Height: 0
```

---

## 4. Test Suite Pass Criteria

| Checkpoint | Target | Verified Output |
| :--- | :--- | :--- |
| **`test_crypto.py`** | Crypto Pipeline | `100% PASS` |
| **`test_core.py`** | Serialization & Consensus | `100% PASS` |
| **`test_p2p.py`** | Framing & Wire | `100% PASS` |
| **`test_pqc_dualpow_sv2.py`** | ML-DSA, Dual-PoW & SV2 | `100% PASS (9/9)` |
| **`test_adversarial_qty4.py`** | Hostile Vector Rejection | `100% PASS (10/10)` |
| **`test_dualpow_security_simulation.py`** | Lane Survival & Anti-Grinding | `100% PASS (3/3)` |
| **`test_functional_stratum.py`** | Stratum V1 Pool Engine | `100% PASS` |
| **`test_functional_mining.py`** | Mining & Subsidy | `100% PASS` |
| **`test_functional_wallet.py`** | HD Wallet & Tx Relay | `100% PASS` |
| **`test_functional_p2p.py`** | Multi-Node Relay | `100% PASS` |
| **`test_functional_reorg.py`** | Deep 10-Block Reorg | `100% PASS` |
| **`test_multinode_stress.py`** | 500-TX Saturation & Chaos | `100% PASS (4/4)` |
| **`test_runner.py`** | Consolidated Suite | `100% PASS (0 Failures)` |
