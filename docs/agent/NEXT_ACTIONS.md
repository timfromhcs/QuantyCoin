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
