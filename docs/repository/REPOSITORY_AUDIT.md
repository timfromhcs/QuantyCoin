# QuantyCoin Comprehensive Repository Forensic Audit

**Audit Date**: 2026-09-05  
**Contract ID**: `QUANTYCOIN-REPO-REVAMP-2026`  
**Auditor**: Autonomous Protocol Engineering Agent  
**Standard**: Absolute Truth & Verification Policy (AR001 - AR016)  

---

## 1. Current Public Positioning

QuantyCoin currently positions itself in its public README as a "High-Performance Quantum & AI Era Layer-1 Blockchain", "Mainnet v7.0", claiming "instantaneous settlement, post-quantum cryptographic security, and enterprise AI-era data throughput delivering thousands of transactions per second".

### Assessment
This positioning suffers from hype-driven terminology ("enterprise AI-era data throughput", "instantaneous settlement") and unsupported performance assertions that are not backed by reproducible production benchmarks. Furthermore, the versioning label ("v7.0.0") misrepresents the protocol baseline which has been rebuilt and frozen as QuantyCoin 2.0 (`QTY2`, Protocol Version `70020`).

---

## 2. Actual Project Scope

The codebase consists of two distinct architectural implementations:
1. **Python Layer-1 Protocol Stack (Active / Verified)**:
   - Location: `core/`, `crypto/`, `network/`, `node/`, `wallet/`, `miner/`, `ui/`, `tests/`
   - Algorithm: Authoritative SHA-256D Proof-of-Work
   - Retargeting: LWMA-1 (window: 45 blocks)
   - Cryptography: Pure Secp256k1 (RFC 6979), Ed25519, BIP39, BIP44, Bech32 (`qty1q...`)
   - Networking: Full-mesh binary P2P framing (`QUAN` / `0x5155414E`), inventory relay, peer scoring
   - Mining: Block template generation (`getblocktemplate`), solo mining, and Stratum V1 TCP pool server (port 3333)
   - Applications: Native Qt6 Desktop applications (Full Wallet, Light Wallet, Node Manager, Miner, Master Suite)
2. **C++ Core Reference Fork (Historical / In-Progress)**:
   - Location: `src/` (derived from Bitcoin Knots / Bitcoin Core)
   - Features vendored CRYSTALS-Dilithium reference code, experimental P2QRH address opcodes, and incomplete audit remediations (`AUDIT_REMEDIATION_VERIFICATION.md`).

---

## 3. Verified Features

The following features have direct, passing execution evidence in `tests/test_runner.py` and `tests/test_multinode_stress.py`:
- [x] **SHA-256D PoW Consensus**: Deterministic 80-byte header hashing and validation.
- [x] **Air-Gapped Genesis Block**: Verifiably mined, independently reproduced, and asserted at node runtime (`GENESIS_HASH = 00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`).
- [x] **LWMA-1 Difficulty Adjustment**: Single-block linear-weighted moving average retargeting with oscillation clamping.
- [x] **Transaction Serialization**: Full SegWit BIP141 witness serialization and TxID calculation.
- [x] **Chainstate & UTXO Engine**: Atomic block connection, disconnection, undo journals, and 10-block deep reorganization recovery.
- [x] **P2P Wire Protocol**: Handshake (`version`/`verack`), `ping`/`pong`, `inv`/`getdata`/`block`/`tx` relay across multi-node topologies.
- [x] **Mempool Ingestion & Double-Spend Defense**: 500-transaction burst saturation (16 TX/sec) and deterministic double-spend rejection.
- [x] **Stratum V1 Pool Protocol**: Socket server on port 3333 supporting `mining.subscribe`, `mining.authorize`, `mining.submit`, and share tracking.
- [x] **HD Wallet**: BIP39 24-word seed generation, BIP44 derivation (`m/44'/999'/0'/0/0`), and Native Bech32 address encoding.
- [x] **Multi-Threaded JSON-RPC**: `getblockchaininfo`, `getmininginfo`, `getblocktemplate`, `submitblock`, `generatetoaddress`, etc.

---

## 4. Unsupported Claims

The following claims in the current repository documentation cannot be supported by empirical evidence and must be removed or rewritten:
1. *"delivering thousands of transactions per second on native Layer-1"*:
   - Reality: Single-threaded Python test loop achieves ~16 TX/s mempool ingestion and ~200-500 block validation TX/s. The 32 MB block capacity allows high data volume, but multi-thousand TPS has never been benchmarked on a live multi-node network.
2. *"enterprise AI-era data throughput"*:
   - Reality: Vague marketing adjective with no cryptographic or protocol meaning.
3. *"instantaneous settlement"*:
   - Reality: Target block interval is 60 seconds; finality requires block confirmation and PoW depth.
4. *"Stratum V1/V2 pool server"*:
   - Reality: Stratum V1 is implemented; Stratum V2 is only an architectural concept / future extension point.
5. *"Quantum-Resilient & Post-Quantum Cryptographic Security"* (in Python layer):
   - Reality: The active Python stack uses classical Secp256k1 ECDSA and Bech32. Post-quantum Dilithium exists only as vendored C++ code in `src/`, with known audit findings documented in `AUDIT_REMEDIATION_VERIFICATION.md`.

---

## 5. Outdated Claims

1. **Version Labels**: References to "v7.0.0", "Mainnet v7.0", and "Protocol Version 70015".
   - Correction: The protocol is QuantyCoin 2.0 (`QTY2`), protocol version `70020`.
2. **Old Genesis Coordinates**: Previous documentation cites hash `00000630...` and timestamp `1771804800`.
   - Correction: Production Genesis block hash is `00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba`, timestamp `1788600000`.
3. **Old Creator Payout Address**: Documentation references `qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g`.
   - Correction: Active Genesis payout address is `qty1qh46xnlu649ug0yfpw7f93xn9dtg90z8hukfsy4`.
4. **LWMA Window**: README states "computed over 144 blocks"; implementation uses `n=45` blocks.

---

## 6. Conflicting Claims

- `README.md` claims version `7.0.0`.
- `CHANGELOG.md` stops at `2.3.0`.
- `core/genesis_constants.py` and `public_genesis.json` define protocol version `70020` and version `2.0.0`.
- `src/` contains an autotools C++ codebase claiming Bitcoin Knots derivation, while root entrypoints (`quantyd_cli.py`, `quanty_node_app.py`) run the native Python codebase.

---

## 7. Missing Trust Documents

The repository lacks dedicated top-level trust and verification files:
- Missing: `TRUST.md` (Explicit trust boundaries, what is verified vs experimental)
- Missing: `THREAT_MODEL.md` (Adversarial security analysis, bounded inputs)
- Missing: `VERIFICATION.md` (Step-by-step reproducible proof instructions)
- Missing: `REPRODUCIBILITY.md` (Build environment determinism)
- Missing: `RELEASE_PROCESS.md` (Release signing and packaging pipeline)
- Missing: `ARCHITECTURE.md` (Formal technical subsystem breakdown)
- Missing: `ROADMAP.md` (Realistic, evidence-based milestone tracker)

---

## 8. Missing Onboarding Guides

- **User**: No step-by-step non-developer guide for downloading, running the wallet, receiving funds, and verifying balances.
- **Miner**: Incomplete instructions on how to configure worker threads, connect an ASIC miner to Stratum port 3333, or solo mine via RPC.
- **Developer**: No guide explaining how to spin up a private 3-node regtest cluster or run targeted integration tests.

---

## 9. Documentation Debt

- Over 15 loose markdown files clutter the repository root (`AUDIT_REMEDIATION_VERIFICATION.md`, `MAINNET_AUDIT_MATRIX.md`, `QT_WALLET_P2MR_AUDIT_FINDINGS_...`, `WHITEPAPER_INTEGRATION_DESIGN.md`, `PHASE6_COMPLETE_SUMMARY.md`, etc.).
- These documents contain important historical context and security audits, but make the root directory disorganized and intimidating to newcomers.

---

## 10. Repository Structure Problems

- Root directory contains mixed shell scripts (`mainnet_commands.sh`, `rename.sh`, `run_p2mr_rpc_e2e.sh`, `test_dilithium_sendmany.sh`), Python entrypoints, build stubs, and audit notes.
- Recommended structure: Group documentation logically under `docs/` (`docs/architecture/`, `docs/protocol/`, `docs/security/`, `docs/verification/`, `docs/operations/`, `docs/development/`, `docs/archive/`).

---

## 11. SEO Problems

- Current keywords rely heavily on buzzwords ("quantum", "AI era") without sufficient technical density on search terms users actually query: "SHA-256 cryptocurrency node", "Stratum V1 server Python", "LWMA difficulty retargeting", "BIP39 HD wallet implementation".

---

## 12. Discoverability Problems

- External links (e.g. `https://quantycoin.org`) may be unhosted or non-functional.
- `llms.txt` and `llms-full.txt` describe outdated v7.0 parameters instead of the frozen QTY2 consensus baseline.

---

## 13. Visual Problems

- Heavy reliance on neon cyberpunk emojis and multi-colored shields badges.
- Badges display hardcoded values (e.g. `tests-100% PASS`) rather than verifiable dynamic indicators.
- Lack of clean, professional diagrams illustrating the actual architecture.

---

## 14. Release Problems

- `README.md` lists downloadable Windows, Linux, and macOS release binaries with specific `.exe` and `.deb` filenames that do not exist as GitHub releases for v2.0.0.
- Releases must be presented with exact status: source-first repository with release packaging scripts provided.

---

## 15. Security Communication Gaps

- `SECURITY.md` is only 22 lines long and lists supported version `7.0.x`.
- Threat model, attack surface analysis, and cryptographic assumptions are not documented in a formal `THREAT_MODEL.md`.
