# QuantyCoin 2.0 (QTY2) Execution Evidence Log

Every major milestone must have concrete, reproducible execution evidence recorded here.

---

## 1. Vault Provisioning
- **Timestamp**: 2026-09-05T10:22:38+02:00
- **Path**: `%USERPROFILE%\Desktop\QuantySecrets\QuantyCoin\`
- **Subdirectories Verified**:
  - `genesis/`
  - `genesis/working/`
  - `genesis/generated/`
  - `genesis/verification/`
  - `genesis/archive/`
  - `signing/`
  - `release/`
  - `manifests/`
- **Result**: Successfully created and verified. Legacy secret file archived in `genesis/archive/`.

---

## 2. Zero-Leak Git Policy Enforcement
- **Timestamp**: 2026-09-05T10:23:54+02:00
- **Modified**: `.gitignore`
- **Protected Patterns Added**:
  - `QuantySecrets/`, `quantysecrets/`
  - `*.secret`, `*.secrets`, `*.private`, `*.key`, `*.pem`, `*.seed`, `*.mnemonic`, `*.wallet`
  - `genesis/working/`, `genesis/generated/private/`, `genesis/verification/private/`, `genesis/archive/private/`
  - `bitcoin knots reference don't push with repo in the end/`
- **Result**: `git status` clean, untracked reference directory properly ignored.

---

## 3. Dedicated V2 Branch
- **Timestamp**: 2026-09-05T10:23:51+02:00
- **Branch**: `v2.0`
- **Command**: `git checkout -b v2.0`
- **Result**: Created and switched to `v2.0`.

---

## 4. Air-Gapped QTY2 Genesis Block Generation & Verification
- **Timestamp**: 2026-09-05T10:25:08+02:00
- **Script**: `scripts/generate_and_verify_genesis.py`
- **Consensus Parameters**:
  - `protocol_version`: 70020
  - `chain_id`: `quantycoin-2.0`
  - `network_magic`: `0x5155414e` (`QUAN`)
  - `genesis_hash`: `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`
  - `merkle_root`: `ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f`
  - `timestamp`: 1788600000 ("2026-09-05: QuantyCoin 2.0 - SHA256D Layer-1 Autonomous Blockchain Protocol")
  - `nonce`: 333641
  - `bits`: 504365055 (`0x1e0fffff`)
  - `payout_address`: `qty1qh46xnlu649ug0yfpw7f93xn9dtg90z8hukfsy4`
- **Verification Evidence**:
  - Independent clean regeneration: PASS
  - Double SHA-256 PoW target check: PASS
  - Merkle root integrity: PASS
  - Block serialization & deserialization roundtrip: PASS (246 bytes)
  - Public manifest export: `genesis/PUBLIC_GENESIS_MANIFEST.json`
  - Air-gapped secret isolation: Key material stored only in `%USERPROFILE%\Desktop\QuantySecrets\QuantyCoin\genesis\generated\`

---

## 5. Mandatory Genesis Runtime Assertions
- **Timestamp**: 2026-09-05T10:25:27+02:00
- **Component**: `node/chainstate.py`
- **Assertions Enforced**:
  - `genesis_header.hash_hex == GENESIS_HASH`
  - `genesis_header.verify_pow()`
  - `genesis_block.verify_merkle_root()`
- **Result**: Verified runtime startup on `Chainstate()`.

---

## 6. Zero-Leak Security Scanner Verification
- **Timestamp**: 2026-09-05T10:25:23+02:00
- **Script**: `scripts/verify_security.py`
- **Result**: [PASS] No secrets, private credentials, or forbidden files detected in tree or git status.

---

## 7. Comprehensive Test Suite Execution (100% Pass)
- **Timestamp**: 2026-09-05T10:29:22+02:00
- **Runner**: `python tests/test_runner.py`
- **Suite Results**:
  - Cryptographic verification suite: [PASS]
  - Core transaction & consensus suite: [PASS]
  - P2P protocol serialization suite: [PASS]
  - Mining & Subsidy Test (2 nodes, P2P sync, balance 300 QTY): [PASSED]
  - Wallet & BIP39 Transaction Test (2 nodes, HD wallet, mempool sync, 25 QTY tx): [PASSED]
  - P2P Multi-Node Relay Test (3 nodes full mesh, bidirectional relay): [PASSED]
  - Chain Split & Deep Reorg Test (2 partitioned nodes, branch lengths 2 vs 4, atomic reorg): [PASSED]
- **Execution Time**: 130.17 seconds
- **Pass Rate**: 100% (0 failures)

---

## 8. Multi-Node Stress, Ingestion & P2P Chaos Matrix (100% Pass)
- **Timestamp**: 2026-09-05T10:32:39+02:00
- **Runner**: `python tests/test_multinode_stress.py`
- **Matrix Results**:
  - Test 1 (Mempool Saturation): 500/500 cryptographically signed transactions ingested and fee-sorted in 32.08s (16 TX/sec): [PASS]
  - Test 2 (Chain Split & Reorg): Branch A (5 blocks) vs Branch B (7 blocks), automatic cumulative PoW reorg to Height 10: [PASS]
  - Test 3 (Double-Spend Rejection): Immediate deterministic rejection of conflicting mempool transactions: [PASS]
  - Test 4 (P2P Network Chaos & Rapid Socket Recovery): Simulated socket kill on live nodes, autonomous peer discovery and reconnect in <3s: [PASS]
- **Pass Rate**: 100% (0 deadlocks, 0 race conditions, 0 failures)


