# QuantyCoin 2.0 (QTY2) Architectural Decisions & Protocol Freeze Records

All immutable protocol parameters and key architectural choices are recorded here.

---

## 1. Protocol Architecture Overview

- **Protocol Version**: `QTY2` (`70020`)
- **Proof-of-Work**: SHA-256D (Double SHA-256)
- **Difficulty Adjustment Algorithm**: LWMA-1 (Linear-Weighted Moving Average, window: 45 blocks, bounded oscillation clamping)
- **Target Block Interval**: 60 seconds (1 minute)
- **Genesis Block Reward**: 50 QTY (5,000,000,000 satoshis)
- **Subsidy Halving Interval**: 2,100,000 blocks (~4 years)
- **Maximum Supply**: 21,000,000 QTY (2,100,000,000,000,000 satoshis)
- **Maximum Block Size**: 32 MB (33,554,432 bytes)
- **Coinbase Maturity**: 100 blocks
- **Smallest Unit**: 1 Satoshi (1 QTY = 100,000,000 Satoshis)
- **Network Magic Bytes**:
  - Mainnet: `0x5155414e` (`QUAN`)
  - Testnet: `0x54515541` (`TQUA`)
  - Regtest: `0x52515541` (`RQUA`)
- **Default Ports**:
  - Mainnet: P2P `19888`, RPC `19889`, Stratum `3333`
  - Testnet: P2P `29888`, RPC `29889`, Stratum `13333`
  - Regtest: P2P `39888`, RPC `39889`, Stratum `23333`
- **Address Encodings**:
  - Native Bech32 Prefix: `qty` (Mainnet), `tqty` (Testnet), `rqty` (Regtest)
  - Legacy Base58 P2PKH Prefix: `0x3a` (Starts with 'Q')
  - Legacy Base58 P2SH Prefix: `0x44` (Starts with 'T')
  - BIP32 HD Extended Public Key: `qpub` (`0x0488B21E`), Private: `qprv` (`0x0488ADE4`)
  - URI Scheme: `quantycoin:`
- **Post-Quantum Cryptography Architecture (NIST FIPS 204 ML-DSA-44)**:
  - NIST Category 2 (ML-DSA-44 / CRYSTALS-Dilithium2) selected for optimal L1 transaction throughput, compact 1312-byte public keys, and 2420-byte signatures.
  - Three distinct authorization modes:
    - Mode 0: `LEGACY_ECDSA` (Secp256k1, witness v0, prefix `qty1q...`)
    - Mode 1: `HYBRID` (Secp256k1 + ML-DSA-44, witness v2, prefix `qty1z...`)
    - Mode 2: `ML_DSA` (Pure ML-DSA-44, witness v1, prefix `qty1p...`)
  - Domain-separated sighash: `SHA256("QUANTYCOIN_PQC_SIGHASH_V1" || sig_type || BIP143_hash)`
  - Native C library `libqtydilithium` with strict fail-closed consensus (zero insecure pseudo-crypto fallbacks).


- **Dual Proof-of-Work Mining Architecture**:
  - Header Format: Standard 80-byte header preserved (`pow_type` encoded in upper 16 bits of `version`).
  - **Lane A (`SHA256D_ASIC`)**: Double-SHA256, 100% subsidy, thermodynamic weight $W_A = 1$.
  - **Lane B (`GENERAL_PURPOSE`)**: RFC 7914 Scrypt ($N=1024, r=1, p=1$, salt `quantycoin_pow_gp`), 50% subsidy, thermodynamic weight $W_B = 2048$.
  - **Difficulty Adjustment**: Independent per-lane LWMA-1 retargeting ($N=45$) with 120-second target spacing per lane, yielding a combined 60-second block time.
  - **Thermodynamic Chainwork Fork Choice**: $\text{work}(B) = \lfloor \frac{2^{256}}{\text{target} + 1} \rfloor \times W_{\text{lane}}$. Block count confers 0 fork advantage; only cumulative physical work advances consensus.

- **Stratum V2 Native Mining Engine**:
  - Binary framing (6-byte header) on port 3334 (`SV2_DEFAULT_PORT`).
  - Native channel multiplexing with dual-lane negotiation (`pow_lane` in `SetupConnection` and `OpenStandardMiningChannel`).
  - Real-time job distribution and share submission with low-latency `SetNewPrevHash`.

---

## QTY4 Hardening Addendum (2026-09-05, branch `feature/qty4-consensus-rebuild`)

- **No consensus change**: all work below is verification/test/CI/supply-chain only.
  `core/genesis_constants.py` and consensus parameters untouched.
- **D1 - Canonical protocol truth gate**: new `scripts/verify_protocol_truth.py`
  cross-checks all 6 `spec/qty4/*.json` files against runtime constants,
  production subsidy/halving boundaries, target codec, network/address/witness
  constants, fork-choice rule, and vector corpus presence. Fails closed on drift.
- **D2 - Independent reference implementation**: new stdlib-only
  `reference/qty4_reference.py` (no imports from `core/`/`crypto/`/`network/`),
  differentially tested by `tests/test_reference_differential_qty4.py`
  (compact, work, subsidy, money-range, MTP, varint, merkle/txid, header,
  addresses, fork-choice). Catches duplicated-bug class failures.
- **D3 - Deterministic fuzz smoke**: new `tests/test_fuzz_qty4.py`
  (seeded, bounded, stdlib-only) covering headers, compact codec, transactions,
  addresses, P2P frames, Stratum V2 frames, varint, plus production-vs-reference
  differential fuzz. Failing inputs preserved under `tests/fuzz_corpus/`.
- **D4 - Supply chain**: `scripts/generate_sbom.py` (deterministic SBOM +
  SHA256SUMS, regenerated in CI as an uploaded artifact, `sbom/` git-ignored),
  `.github/dependabot.yml` (pip + GitHub Actions weekly), and
  `.github/workflows/codeql.yml` (CodeQL python analysis on push/PR/weekly).
- **D5 - CI gates**: `ci.yml` now runs native-backend load check, protocol-truth,
  reference-differential, and fuzz-smoke jobs; `build.yml` verifies the native
  backend on both OSes and generates/uploads the SBOM; `security.yml` gains an
  SBOM supply-chain job.
