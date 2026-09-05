# QuantyCoin Protocol Initial Truth Matrix & Forensic Ledger

**Audit Scope**: Repository forensics prior to QTY3 Transformation  
**Timestamp**: 2026-09-05T12:36:00+02:00  
**Current Branch**: `feature/qty3-pq-dualpow-sv2` (SHA: `03ab40d`)  
**Base Branch**: `main` (SHA: `847731d`)  

---

## 1. Forensic Claim vs Reality Truth Matrix

| Feature / Subsystem | Claimed Status | Actual Implementation Reality | Authoritative Code Path | Executable Tests | Discrepancies & Contradictions | Required Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PQC Algorithm Set** | FIPS 204 ML-DSA-65 (1952 pk, 3309 sig) | Genuine FIPS 204 ML-DSA-44 / Dilithium2 (1312 pk, 2420 sig) via `libqtydilithium.dll` | `crypto/mldsa.py`, `src/crypto/dilithium_wrapper.c` | `tests/test_pqc_dualpow_sv2.py` | Documentation & README erroneously labeled ML-DSA-44 as ML-DSA-65. R002 / R009 violation. | Correct all labels to ML-DSA-44 / Dilithium2 across specs, README, and RPC telemetry. |
| **PQC Pseudo-Crypto Fallback** | "Zero-mock with fallback" | Insecure `_fallback_*` completely excised. Fail-closed on missing DLL via `CryptographicBackendUnavailableError`. | `crypto/mldsa.py` | `tests/test_pqc_dualpow_sv2.py` (test_07) | None. Insecure fallbacks permanently eliminated in `03ab40d`. | Keep strict native requirement and verify in cleanroom. |
| **PoW Lane A (ASIC)** | Double SHA-256D, 100% subsidy, weight $W_A=1$ | Verified double-SHA256 evaluation, 50 QTY base reward, weight 1. 80-byte header with `version >> 16 == 0`. | `core/block.py`, `core/consensus.py` | `tests/test_functional_mining.py`, `tests/test_pqc_dualpow_sv2.py` | None. 100% compliant with physical ASIC header standards. | Maintain compatibility. |
| **PoW Lane B (CPU/GPU)** | Mature general-purpose algorithm (Scrypt 1024), 50% subsidy, weight $W_B=2048$ | RFC 7914 Scrypt ($N=1024, r=1, p=1$, salt `quantycoin_pow_gp`), 25 QTY reward, weight 2048. | `core/block.py`, `core/consensus.py` | `tests/test_pqc_dualpow_sv2.py` (test_02) | None. ASIC resistance verified via 128KB memory hardness. | Retain and document CPU/GPU capabilities. |
| **Fork Choice & Chainwork** | Cumulative thermodynamic chainwork | Chain selection strictly follows $\sum W_{\text{lane}} \cdot \lfloor 2^{256} / (T+1) \rfloor$. Block count conveys 0 advantage. | `node/chainstate.py` | `tests/test_pqc_dualpow_sv2.py` (test_03, test_09) | None. Low-difficulty spam attack mathematically defeated and verified. | Retain as inviolable consensus rule. |
| **Stratum V2 Protocol** | Production binary protocol engine | 6-byte binary framing on port 3334 (`SV2_DEFAULT_PORT`), dual-lane multiplexing, low-latency prevhash. | `miner/stratum_v2.py` | `tests/test_pqc_dualpow_sv2.py` (test_04) | README planned section still listed Stratum V2 as "Planned". Stale claim! | Reclassify Stratum V2 as VERIFIED in README. |
| **Quantum Migration** | Phased migration from legacy ECDSA | `get_quantum_vulnerability_report()` and `build_pqc_migration_transaction()` operational in `HDWallet`. | `wallet/hd_wallet.py` | `tests/test_pqc_dualpow_sv2.py` (test_06) | Needs prominent user-facing explanation in README and Trust Center. | Document migration rules truthfully. |
| **Protocol Versioning** | QTY2 vs QTY3 | Code uses protocol 70020 with dual-PoW and PQC. Contract designates evolution as QTY3 Mainnet. | `core/genesis_constants.py`, `docs/agent/CONSENSUS_FREEZE.md` | `tests/test_runner.py` | Formalize QTY3 protocol specifications and consensus parameter freeze. | Author `QTY3_PROTOCOL_FREEZE.md`. |

