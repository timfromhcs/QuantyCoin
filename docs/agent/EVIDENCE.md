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

---

## 9. Repository Revamp & Claim Audit Verification (QUANTYCOIN-REPO-REVAMP-2026)
- **Timestamp**: 2026-09-05T10:52:15+02:00
- **Auditor**: Autonomous Protocol Rebuild Agent
- **Artifacts Generated**:
  - `docs/repository/REPOSITORY_AUDIT.md`: 15-point forensic audit of repository structure, codebases, trust vectors, and public claims.
  - `docs/repository/CLAIM_LEDGER.md`: Classification of 15 high-impact public claims into VERIFIED, IMPLEMENTED, EXPERIMENTAL, PLANNED, UNKNOWN, BLOCKED with replacement text.
  - `README.md`: Evidence-based rewrite with verified consensus parameters, truth table, Mermaid architecture, tested quickstart commands, and zero fabricated claims.
  - `TRUST.md`: Trust center establishing code integrity, consensus authority, air-gapped genesis custody, and reproducible verification.
  - `SECURITY.md`: Vulnerability disclosure policy, QTY2 consensus threat boundaries, and reporting protocols.
  - `THREAT_MODEL.md`: STRIDE analysis, consensus attack vectors, 51% defense via LWMA, and Sybil protection.
  - `VERIFICATION.md`: Independent verification guide for genesis, consensus rules, cryptographic signatures, and network protocol.
  - `REPRODUCIBILITY.md`: Deterministic build and execution instructions across environments.
  - `RELEASE_PROCESS.md`: Release lifecycle, tag signing, binary provenance, and changelog management.
  - `ARCHITECTURE.md`: Layered system topology distinguishing Python Layer-1 operational network from C++ reference tree.
  - `ROADMAP.md`: Realistic, phased development milestones with explicit technical dependencies.
  - `docs/index.md`: Central documentation hub organizing 8 categorical directories (`architecture`, `protocol`, `security`, `verification`, `operations`, `development`, `repository`, `archive`).
  - `docs/USER_GUIDE.md`: Executable guide for node deployment, wallet creation, and transaction transfer.
  - `docs/MINER_GUIDE.md`: Authoritative mining guide for solo mining, Stratum V1 mining pool connectivity, and hardware sizing.
  - `docs/DEVELOPER_GUIDE.md`: Architecture reference, RPC documentation, testing instructions, and contribution protocols.
  - `docs/project-summary.md`: SEO and machine-readable project digest.
  - `llms.txt`: Structured discovery manifest for LLMs and autonomous agents.
  - `CITATION.cff`: Formal academic and software citation metadata.
  - `.github/copilot-instructions.md` & `.github/instructions/`: Autonomous and human AI agent onboarding constraints.

---

## 10. Link Integrity & Documentation Execution Evidence
- **Timestamp**: 2026-09-05T10:48:30+02:00
- **Link Validator Script**: Internal regex AST validator across all repository `.md` files.
- **Link Audit Results**:
  - Total internal markdown links verified: 67
  - Broken links detected: 0 (100% resolve)
- **Documentation Command Verification**:
  - `python scripts/verify_security.py`: [PASS] 0 leaks detected.
  - `python tests/test_crypto.py`: [PASS] BIP39, Secp256k1, address encoding verified.
  - `python tests/test_core.py`: [PASS] Transaction, block, and script serialization verified.
  - `python tests/test_p2p.py`: [PASS] P2P network framing and message roundtrip verified.
  - `python tests/test_functional_stratum.py`: [PASS] Stratum V1 mining pool subscription, authorization, and share submission verified.
  - Genesis verification snippet: [PASS] Double-SHA256 hash matches `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`.
  - `Chainstate()` standalone initialization: [PASS] Genesis assertions passed, height 0 confirmed.

---

## 11. Cloud CI/CD Execution & PR Finalization Evidence (QUANTYCOIN-QTY2-FINALIZE-PR-2026)
- **Timestamp**: 2026-09-05T11:09:00+02:00
- **Auditor**: Autonomous Protocol Rebuild Agent
- **Target Branch**: `v2.0`
- **Base Branch**: `main`
- **GitHub Actions Run ID**: `33956695355`
- **Cloud Run Outcome**: **100% PASS** across all 10 platform matrix jobs:
  - Zero-Leak Git Policy & Secret Scanner (Ubuntu 22.04): [PASS] (7s)
  - Ubuntu 22.04 - Python 3.10: [PASS] (2m 45s)
  - Ubuntu 22.04 - Python 3.11: [PASS] (2m 21s)
  - Ubuntu 22.04 - Python 3.12: [PASS] (1m 55s)
  - Windows Server 2022 - Python 3.10: [PASS] (3m 12s)
  - Windows Server 2022 - Python 3.11: [PASS] (2m 44s)
  - Windows Server 2022 - Python 3.12: [PASS] (3m 07s)
  - macOS 14 (Apple Silicon) - Python 3.10: [PASS] (9m 59s)
  - macOS 14 (Apple Silicon) - Python 3.11: [PASS] (9m 31s)
  - macOS 14 (Apple Silicon) - Python 3.12: [PASS] (9m 37s)
- **CI/CD Consolidation**:
  - Consolidated into exactly 5 canonical workflows: `ci.yml`, `build.yml`, `security.yml`, `documentation.yml`, `release.yml`.
  - Removed obsolete/broken Knots workflows (`build-and-address-tests.yml`).
- **Community Health & Documentation**:
  - Created `SUPPORT.md` with explicit security disclosure pathways.
  - Updated `CONTRIBUTING.md` with full local pre-PR verification command checklist.
  - Implemented `scripts/verify_documentation.py` (84 links verified, 0 broken).
  - Implemented `scripts/verify_genesis.py` (100% independent genesis check with 0 secret dependencies).
- **PR Preparation Status**: Ready for reviewable pull request submission from `v2.0` into `main`.

---

## 12. Final Repository Hardening Evidence (QUANTYCOIN-QTY2-REPO-HARDENING-2026)
- **Timestamp**: 2026-09-05T11:22:00+02:00
- **Auditor**: Autonomous Protocol Rebuild Agent
- **Target Branch**: `v2.0`
- **Base Branch**: `main`
- **Verification Evidence**:
  - **Zero-Leak Security Scanner (`scripts/verify_security.py`)**:
    ```
    QUANTYCOIN ZERO-LEAK SECURITY SCANNER
    [PASS] No secrets, private credentials or forbidden files detected.
    ```
  - **Genesis Cryptographic Audit (`scripts/verify_genesis.py`)**:
    ```
    QTY2 INDEPENDENT GENESIS CRYPTOGRAPHIC AUDIT
    [PASS] Manifest validated: PUBLIC_GENESIS_MANIFEST.json
    [PASS] Manifest validated: public_genesis.json
    [PASS] Chainstate genesis assertions verified.
    [PASS] Block header PoW & Merkle root calculation verified.
           Genesis Hash: 00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba
           Merkle Root:  ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f
           Difficulty:   0x1e0fffff
    GENESIS INDEPENDENT AUDIT PASSED WITH 100% SUCCESS
    ```
  - **Documentation Link Integrity (`scripts/verify_documentation.py`)**:
    ```
    Scanning 64 markdown files for link integrity...
    Validated 85 local relative links across repository.
    [PASS] All markdown links resolve successfully.
    [PASS] llms.txt validated.
    [PASS] CITATION.cff validated.
    ALL DOCUMENTATION VALIDATION CHECKS PASSED (100%)
    ```
  - **Legacy "v7" Eradication**:
    - Audited and updated `node/daemon.py`, `node/rpc_server.py`, `ui/node_gui.py`, all Qt6 apps, `start_quantycoin.bat`, `llms-full.txt`, and packaging scripts.
    - Verified 0 remaining stale v7 references across active codebase.
  - **Error Masking Elimination**:
    - Removed all `|| true` constructs in `packaging/linux/build_deb.sh`, `packaging/macos/build_dmg.sh`, and `.github/workflows/release.yml`.
  - **Brand System Asset Delivery**:
    - Vector SVGs generated: `brand/logo.svg`, `brand/logo-mark.svg`, `brand/wordmark.svg`, `brand/monochrome.svg`, `brand/favicon.svg`.
    - Raster cards generated: `brand/social-preview.png` (1200x630, 44,805 bytes), `brand/github-social-preview.png` (1280x640, 44,694 bytes).
    - Design manual: `brand/brand-guidelines.md`.
  - **README Presentation Hardening**:
    - Strictly conformed to the 19 required sections.
    - Embedded official `brand/logo.svg`.
    - Honest Nakamoto PoW throughput benchmarks documented (14-28 TPS, 16 TX/s mempool benchmark).
    - Dynamic verification badges linked.

---

## 11. Post-Quantum Cryptography, Dual-PoW Consensus & Stratum V2 Verification
- **Timestamp**: 2026-09-05T12:03:30+02:00
- **Contract**: `QUANTYCOIN-QTY2-PQC-DUALPOW-SV2-2026`
- **Execution Log (`python tests/test_runner.py`)**:
  ```
  ========================================================
  RUNNING CRYPTOGRAPHIC & CORE UNIT TESTS
  ========================================================
  [PASS] Cryptographic verification suite
  [PASS] Core transaction & consensus suite
  [PASS] P2P protocol serialization suite

  ========================================================
  RUNNING TEST: MiningTest
  ========================================================
  1. Verifying initial Genesis state...
  2. Mining 5 blocks on Node 0...
  3. Synchronizing blocks across P2P wire to Node 1...
  4. Verifying miner coinbase rewards & balance calculation...
  5. Querying mining telemetry & block templates...
  [PASS] MiningTest COMPLETED WITH 100% SUCCESS!

  ========================================================
  RUNNING TEST: WalletTest
  ========================================================
  1. Creating test HD wallets...
  2. Mining 3 blocks to fund Wallet A...
  3. Fetching spendable UTXOs for Wallet A...
  4. Creating & signing 25 QTY transaction from Wallet A -> Wallet B...
  5. Broadcasting transaction to Node 0 mempool...
  6. Synchronizing mempools across P2P network...
  7. Mining 1 block to confirm transaction...
  8. Verifying final confirmed balances...
  [PASS] WalletTest COMPLETED WITH 100% SUCCESS!

  ========================================================
  RUNNING TEST: P2PTest
  ========================================================
  1. Verifying initial P2P mesh network topology...
  2. Verifying protocol version and user agents...
  3. Mining blocks on Node 0 and checking propagation to Node 1 & 2...
  4. Mining 2 blocks on Node 2 and syncing backwards to Node 0 & 1...
  [PASS] P2PTest COMPLETED WITH 100% SUCCESS!

  ========================================================
  RUNNING TEST: ReorgTest
  ========================================================
  1. Mining 3 common base blocks on Node 0 and syncing...
  2. Disconnecting Node 1 to simulate a network split / partition...
  3. Mining Branch A on Node 0 (2 blocks -> Height 5)...
  4. Mining Branch B on Node 1 (4 blocks -> Height 7)...
  5. Reconnecting partition & resolving fork choice...
  6. Verifying that Node 0 reorganized to Branch B (Height 7)...
  [PASS] ReorgTest COMPLETED WITH 100% SUCCESS!

  ========================================================
  RUNNING STRATUM V1 MINING PROTOCOL TEST (Port: 13335)
  ========================================================
    [PASS] 1. mining.subscribe handshake successful
    [PASS] 2. mining.authorize accepted
    [PASS] 3. mining.submit share validated and counted
  ALL STRATUM V1 PROTOCOL TESTS PASSED WITH 100% SUCCESS!

  ========================================================
  RUNNING PQC, DUAL-POW & STRATUM V2 PROTOCOL TEST SUITE
  ========================================================
  [PASS] PQC & Hybrid Signature Verification (NIST FIPS 204 ML-DSA & Hybrid Bech32m)
  [PASS] Dual-PoW Lane A & Lane B Mining & Verification (SHA256D ASIC & Scrypt 1024 General Purpose)
  [PASS] Cumulative Thermodynamic Chainwork Calculations (W_A = 1, W_B = 2048)
  [PASS] Stratum V2 Binary Framing & Dual-Lane Multiplexing (Port 19445)
  [PASS] New Protocol RPC Endpoints (getmininglanes, getminingtargets, getchainwork, getnewpqaddress, getaddressinfo, getstratuminfo)
  [PASS] HDWallet Post-Quantum Key Derivation & Transaction Creation (qty1p... & qty1z...)
  [PASS] Strict Rejection of Pseudo-Crypto & Malleated Signatures
  [PASS] Cross-Mode Signature Replay Attack Prevention
  [PASS] Thermodynamic Chainwork Defeats Low-Difficulty Spam Attack

  ========================================================
             QUANTYCOIN TEST SUITE RESULTS
  ========================================================
   - Mining & Subsidy Test               : [PASSED]
   - Wallet & BIP39 Transaction Test     : [PASSED]
   - P2P Multi-Node Relay Test           : [PASSED]
   - Chain Split & Deep Reorg Test       : [PASSED]
   - Stratum V1 Protocol Test            : [PASSED]
   - PQC, Dual-PoW & SV2 Test Suite      : [PASSED]
  ========================================================
  ALL TESTS PASSED WITH 100% SUCCESS (0 FAILURES)!
  ========================================================
  ```
- **Security Scanner Proof**:
  - `python scripts/verify_security.py`: `[PASS] No secrets, private credentials or forbidden files detected.` (100% PASS, 0 leaks).
- **Documentation Validator Proof**:
  - `python scripts/verify_documentation.py`: `[PASS] All markdown links resolve successfully. ALL DOCUMENTATION VALIDATION CHECKS PASSED (100%).`

---

## 11. QTY4 Canonical Genesis Audit & GitHub Actions CI Verification
- **Timestamp**: 2026-09-05T18:15:26+02:00
- **Target PR**: PR #11 (`feature/qty4-consensus-rebuild` -> `main`)
- **Canonical Genesis Verifier Execution** (`python scripts/verify_genesis.py`):
  - Gate 1: Stale Artifact & Legacy Contamination Scan: PASS (0 stale files).
  - Gate 2: Runtime Consensus Constants Verification: PASS (`PROTOCOL_VERSION=70040`, `CHAIN_ID=quantycoin-4.0`, `MAGIC=51545934`, `PORTS=19444/19445/3333/3334`, `GENESIS_HASH=000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3`, `MERKLE_ROOT=3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea`).
  - Gate 3: Manifest & Public Artifact Consistency Audit: PASS (`PUBLIC_GENESIS_MANIFEST.json`, `public_genesis.json`, `genesis_hash.txt`, `genesis_merkle_root.txt`).
  - Gate 4: Path A Core State Machine Verification: PASS.
  - Gate 5: Path B Independent Standalone Engine: PASS.
  - Gate 6: Dual-Path Byte-for-Byte Cross Verification: PASS (Exact hash, Merkle root, 267 bytes raw block).
  - Result: `ALL QTY4 GENESIS VERIFICATION GATES PASSED (100%)`.
- **Zero-Leak Security Scanner Execution** (`python scripts/verify_security.py`):
  - `[PASS] No secrets, private credentials or forbidden files detected.` (0 leaks).
- **Adversarial & Unit Verification Suite**:
  - `tests/test_adversarial_qty4.py`: PASS (10/10 attack vectors rejected).
  - `tests/test_crypto.py`: PASS (100%).
  - `tests/test_core.py`: PASS (100%).
  - `tests/test_p2p.py`: PASS (100%).
  - `tests/test_dualpow_security_simulation.py`: PASS (3/3 scenarios).
  - `tests/test_runner.py`: PASS (100%).
  - `tests/test_multinode_stress.py`: PASS (100%).
- **GitHub Actions Cloud CI Matrix (100% PASS Across Windows & Linux)**:
  - `Security & Cryptographic Integrity`: PASS (`Zero-Leak Git Policy & Secret Scanner`, `Genesis PoW & Consensus Verification`).
  - `Documentation & Link Integrity`: PASS (`Markdown Links & Standards Audit`).
  - `Cloud Build & Platform Verification`: PASS (`ubuntu-latest`, `windows-latest`).
  - `CI (Test Matrix & Protocol Validation)`:
    - Ubuntu-latest (Py 3.10, 3.11, 3.12): PASS (100%).
    - Windows-latest (Py 3.10, 3.11, 3.12): PASS (100%).

---

## 12. QTY4 Verification Hardening (protocol truth, reference, fuzz, supply chain)
- **Timestamp**: 2026-09-05 (local, Windows, Python 3.14.6)
- **Branch**: `feature/qty4-consensus-rebuild`
- **Scope**: verification/test/CI/supply-chain only. Zero consensus changes
  (`git diff` touches no file under `core/`, no spec JSON values).
- **Results**:
  - `python scripts/verify_security.py`: PASS (0 leaks).
  - `python scripts/verify_genesis.py`: ALL 6 GATES PASS (dual-path byte identity).
  - `python scripts/verify_protocol_truth.py`: ALL PROTOCOL TRUTH CHECKS PASSED.
  - `python scripts/verify_documentation.py`: 103 links, 0 broken.
  - `python scripts/verify_documentation_consistency.py`: PASS.
  - `python scripts/generate_sbom.py`: 1288 components hashed (artifact git-ignored, CI-uploaded).
  - `python tests/test_crypto.py` / `test_core.py` / `test_p2p.py`: PASS.
  - `python tests/test_adversarial_qty4.py`: 10/10 OK.
  - `python tests/test_reference_differential_qty4.py`: 10/10 OK.
  - `python tests/test_fuzz_qty4.py` (seed 20260905, 2000 iters): ALL PASSED.
  - `python tests/test_dualpow_security_simulation.py`: 3/3 PASS.
  - `python tests/test_functional_stratum.py`: PASS.
  - `python -c "from crypto.mldsa import get_native_lib"`: NATIVE ML-DSA OK (libqtydilithium.dll).
  - `python tests/test_runner.py`: ALL TESTS PASSED (196.82s).
  - `python tests/test_multinode_stress.py`: ALL 4 STRESS TESTS PASSED.
- **CI deltas** (this change): `ci.yml` +protocol-truth, +reference-differential,
  +fuzz-smoke, +native-backend check; `build.yml` +native check, +SBOM;
  `security.yml` +SBOM job; new `codeql.yml`; new `dependabot.yml`.
- **Note**: local Python is 3.14.6 (CI matrix covers 3.10-3.12); cloud run
  verification pending push of this commit.
- **Cloud result (commit 6c1764c, 2026-09-05)**: 5/5 workflows SUCCESS —
  Security & Cryptographic Integrity (run 33978737751),
  Documentation & Link Integrity (33978737789),
  Cloud Build & Platform Verification (33978737802),
  CodeQL Static Analysis (33978737843),
  CI Test Matrix incl. new protocol-truth / reference-differential / fuzz-smoke /
  native-backend steps on all 6 jobs ubuntu+windows × py3.10/3.11/3.12 (33978737891).




