# QuantyCoin 2.0 (QTY2) Next Actions Queue

**Priority Order**:
1. Consensus & Protocol Parameters
2. Genesis Generation & Verification Gate
3. Security & Anti-Leak Validation
4. Network Protocol & P2P
5. Synchronization Engine & Convergence
6. Chainstate, UTXO & Reorg
7. Mining & Stratum Architecture
8. Wallet & Post-Quantum Cryptography
9. RPC Implementation
10. Desktop Applications & UX
11. Packaging & CI/CD
12. Completion Gate & Final Report

---

## Action Plan

- [x] **Step 1: Protocol Parameter Freeze**
  - Define canonical parameters in `docs/agent/DECISIONS.md` and `core/genesis_constants.py`.
  - Fix magic bytes, ports (Mainnet: 19888 P2P / 19889 RPC / 3333 Stratum, Testnet: 29888 / 29889, Regtest: 39888 / 39889).
  - Set block time (60s), initial subsidy (50 QTY), halving schedule (2,100,000 blocks), max supply (21,000,000 QTY).
  - Specify deterministic coinbase message and locktime.

- [x] **Step 2: Air-Gapped Genesis Generation**
  - Implement zero-leak generator targeting `%USERPROFILE%\Desktop\QuantySecrets\QuantyCoin\genesis\`.
  - Ensure working files, nonces, raw outputs stay in `QuantySecrets`.
  - Mine candidate block header satisfying difficulty.
  - Independently regenerate and verify hash, merkle root, and serialization.
  - Export only `genesis/PUBLIC_GENESIS_MANIFEST.json`.
  - Update `core/genesis_constants.py` and `public_genesis.json`.

- [x] **Step 3: Pre-Commit & Pre-Push Security Verifier**
  - Create scripts/verify_security.py to verify no secrets exist in repo or diff.
  - Verify zero leaks before commits and push.

- [x] **Step 4: Consensus & Chainstate Hardening**
  - Ensure transaction serialization, endianness, script verification, and block validation are strictly deterministic.
  - Verify LWMA-1 difficulty adjustment algorithm and clamp rules.
  - Validate atomic connect/disconnect block logic and UTXO rollbacks.

- [x] **Step 5: P2P & Synchronization Engine**
  - P2P message framing: magic, command, length, checksum (hash256[:4]), payload.
  - Handshake (version, verack), ping/pong, addr/getaddr, inv/getdata/block/tx.
  - Header-first sync with locators and reorg recovery.
  - Multi-node convergence test with 3 independent nodes from blank DB.

- [x] **Step 6: SHA256D Mining & Stratum Server**
  - Authoritative mining engine with block template generation and submitblock RPC.
  - Stratum V1 mining pool server (`mining.subscribe`, `mining.authorize`, `mining.notify`, `mining.submit`).
  - Share validation, difficulty scaling, extranonce handling.

- [x] **Step 7: Wallet & Post-Quantum Cryptography**
  - BIP39/BIP44 HD key derivation and encrypted wallet storage.
  - Support for post-quantum signature schemes (CRYSTALS-Dilithium / ML-DSA hybrid) abstraction.
  - Coin selection, change output management, and raw transaction creation.

- [x] **Step 8: RPC Interface Complete Audit**
  - Verify all standard Bitcoin Knots / Core RPCs: `getblockchaininfo`, `getblockcount`, `getbestblockhash`, `getblock`, `getblockhash`, `getrawtransaction`, `sendrawtransaction`, `getrawmempool`, `getmempoolinfo`, `getpeerinfo`, `getnetworkinfo`, `getchaintips`, `getmininginfo`, `getblocktemplate`, `submitblock`, `getwalletinfo`, `getnewaddress`, `getbalance`, `sendtoaddress`, `listtransactions`.

- [x] **Step 9: Desktop Applications & Assets**
  - Native Qt6 UI for Node, Wallet, Miner, and unified Suite.
  - Assets: Logo, QTY icon, splash screen, SVG/PNG/ICO formats.

- [x] **Step 10: Packaging & CI/CD**
  - Multi-platform packaging scripts (Windows MSI/Portable, Linux deb/AppImage/tarball, macOS bundle).
  - GitHub Actions CI matrix with unit, functional, sanitizer, and secret scans.

- [x] **Step 11: Verification & Completion Gate**
  - Run full test suite: unit, functional, p2p, reorg, multinode stress.
  - Record execution proof in `docs/agent/EVIDENCE.md`.
  - Produce `FINAL_IMPLEMENTATION_REPORT.md`.

- [x] **Step 12: Repository Revamp & Presentation Engineering (QUANTYCOIN-REPO-REVAMP-2026)**
  - Comprehensive 15-section forensic audit (`docs/repository/REPOSITORY_AUDIT.md`).
  - High-impact claim ledger classification (`docs/repository/CLAIM_LEDGER.md`).
  - Complete README rewrite with verified truth table, architecture diagrams, and tested quickstart.
  - Dedicated Trust Center suite (`TRUST.md`, `SECURITY.md`, `THREAT_MODEL.md`, `VERIFICATION.md`, `REPRODUCIBILITY.md`, `RELEASE_PROCESS.md`, `ARCHITECTURE.md`, `ROADMAP.md`).
  - Documentation tree restructuring into 8 categorical modules with central hub (`docs/index.md`).
  - Verified, tested user onboarding guides (`docs/USER_GUIDE.md`, `docs/MINER_GUIDE.md`, `docs/DEVELOPER_GUIDE.md`).
  - Machine readability & SEO optimization (`docs/project-summary.md`, `llms.txt`, `CITATION.cff`).
  - Agent instructions & workflow rules (`.github/copilot-instructions.md`, `.github/instructions/`).
  - 100% link resolution and command execution verification.
  - Final report production (`docs/agent/FINAL_REPO_REVAMP_REPORT.md`).

- [x] **Step 13: PR Finalization & Cloud CI/CD Engineering (QUANTYCOIN-QTY2-FINALIZE-PR-2026)**
  - Independent forensic claim re-verification (`docs/agent/FINALIZATION_AUDIT.md`).
  - Cloud CI/CD consolidation into 5 canonical workflows (`ci.yml`, `build.yml`, `security.yml`, `documentation.yml`, `release.yml`).
  - Verification of GitHub Actions run `33956695355` (10/10 jobs passing across Ubuntu, Windows, macOS).
  - Standalone verification tools (`scripts/verify_documentation.py`, `scripts/verify_genesis.py`).
  - Community health enhancement (`SUPPORT.md`, updated `CONTRIBUTING.md`).
  - Full git diff review against `origin/main` (`docs/agent/FINAL_DIFF_REVIEW.md`).
  - Cloud build verification report (`docs/agent/CLOUD_BUILD_VERIFICATION.md`).
  - PR verification packet (`docs/agent/PR_VERIFICATION.md`).
  - Create reviewable pull request from `v2.0` into `main` (NEVER_AUTO_MERGE policy).
  - Final readiness report (`docs/agent/FINAL_PR_READINESS_REPORT.md`).

- [x] **Step 14: Final Repository Hardening (QUANTYCOIN-QTY2-REPO-HARDENING-2026)**
  - Full audit baseline established (`docs/agent/HARDENING_BASELINE.md`).
  - Total eradication of stale legacy "v7" references in node, RPC, UI, launchers, documentation, packaging, and CI.
  - Elimination of error masking (`|| true`) in cloud packaging and workflows.
  - Complete Brand System established in `brand/` (5 SVGs, 2 PNG social previews, `brand-guidelines.md`).
  - Root `README.md` restructured to 19 strictly sequenced sections with honest Nakamoto PoW throughput benchmarks (14-28 TPS) and dynamic badges.
  - Independent verification: zero leaks (`verify_security.py`), genesis audit (`verify_genesis.py`), link validator (`verify_documentation.py`), full test suite (`test_runner.py`).
  - Hardening reports generated: `docs/agent/CLOUD_BUILD_VERIFICATION.md`, `docs/agent/FINAL_DIFF_REVIEW.md`, `docs/agent/FINAL_HARDENING_REPORT.md`, `docs/agent/PR_VERIFICATION.md`.
  - Push to `v2.0` and open PR to `main` with `NEVER_MERGE_MAIN` policy enforced.

- [x] **Step 15: NIST FIPS 204 PQC, Dual-PoW Consensus & Stratum V2 Protocol (QUANTYCOIN-QTY2-PQC-DUALPOW-SV2-2026)**
  - Baseline audit & parameter frozen: `docs/agent/PQC_DUALPOW_BASELINE.md`.
  - 5 Protocol Specifications authored: `PQC_SPEC.md`, `DUAL_POW_SPEC.md`, `CHAINWORK_SPEC.md`, `STRATUM_V2_SPEC.md`, `MIGRATION_SPEC.md`.
  - Native C ML-DSA library compiled (`src/crypto/libqtydilithium.dll`).
  - Upgraded `crypto/bip32_44.py` to BIP 350 Bech32m witness programs (`qty1p...`, `qty1z...`).
  - Implemented multi-mode transaction authorization in `core/transaction.py` (Classical, ML-DSA, Hybrid).
  - 80-byte block header preserved with upper-16-bit `pow_type` encoding in `core/block.py`.
  - Implemented independent per-lane LWMA-1 difficulty adjustment and thermodynamic cumulative chainwork ($W_A=1, W_B=2048$) in `core/consensus.py` and `node/chainstate.py`.
  - Native Stratum V2 binary framing and dual-lane channel multiplexing in `miner/stratum_v2.py`.
  - Dual-lane CPU/GPU miner with CLI flags `--lane` (`sha256d` or `general`) in `miner/engine.py` and `miner/cli.py`.
  - Extended RPC server with `getmininglanes`, `getminingtargets`, `getchainwork`, `getnewpqaddress`, `getaddressinfo`, `getstratuminfo`.
  - 100% verified test suite in `tests/test_pqc_dualpow_sv2.py` and integrated into `tests/test_runner.py`.
  - Security and documentation integrity verified (`verify_security.py` & `verify_documentation.py`).

- [x] **Step 16: Post-Quantum Hardening, Pseudo-Crypto Elimination & Adversarial Gates (QUANTYCOIN-QTY3-PQ-DUALPOW-SV2-MAINNET)**
  - Total elimination of insecure fallback pseudo-crypto (`_fallback_*`) in `crypto/mldsa.py`.
  - Introduced `CryptographicBackendUnavailableError` ensuring fail-closed consensus behavior.
  - Implemented automated legacy UTXO quantum vulnerability audit and migration transactions in `wallet/hd_wallet.py`.
  - Added adversarial attack coverage in `tests/test_pqc_dualpow_sv2.py`: pseudo-crypto rejection, signature non-malleability, cross-mode replay prevention, and thermodynamic chainwork defense against low-difficulty grinding.
  - Authoritative protocol freeze and security gate documentation established: `docs/agent/CONSENSUS_FREEZE.md` and `docs/agent/SECURITY_GATES.md`.
  - Recorded Incident INC-004 in `docs/agent/FAILURES.md`.
  - Verified 100% PASS across full test runner, zero leaks (`scripts/verify_security.py`), and 100% link resolution (`scripts/verify_documentation.py`).

