# QuantyCoin Trust Center

**Last Updated**: 2026-09-05  
**Protocol Version**: QTY3 (`70020`)  
**Core Policy**: Verification Over Marketing  

---

## 1. What is QuantyCoin?

QuantyCoin (QTY) is an independent, open-source Layer-1 cryptocurrency combining asymmetric Dual Proof-of-Work mining (Lane A SHA-256D ASIC & Lane B RFC 7914 Scrypt CPU/GPU), NIST FIPS 204 ML-DSA-44 post-quantum transaction authorization, cumulative thermodynamic chainwork, rapid 60-second combined block intervals, responsive LWMA-1 difficulty retargeting, 32 MB block capacity, native Stratum V2 binary framing and V1 mining pool architecture, BIP39/44 multi-mode HD wallets, and self-sovereign Qt6 desktop suites.

---

## 2. What is Verified

The following components are implemented, tested, and verifiably reproducible directly from this repository:

| Subsystem | Verified State | Test / Verification Command |
| :--- | :--- | :--- |
| **Dual-PoW Consensus (SHA-256D & Scrypt)** | **100% PASS** | `python -m unittest tests/test_pqc_dualpow_sv2.py` |
| **Thermodynamic Chainwork ($W_A=1, W_B=2048$)**| **100% PASS** | `python -m unittest tests/test_pqc_dualpow_sv2.py` |
| **NIST FIPS 204 ML-DSA-44 Signatures** | **100% PASS** | `python -m unittest tests/test_pqc_dualpow_sv2.py` |
| **Stratum V2 Binary Framing (Port 3334)** | **100% PASS** | `python -m unittest tests/test_pqc_dualpow_sv2.py` |
| **Legacy UTXO Quantum Migration** | **100% PASS** | `python -m unittest tests/test_pqc_dualpow_sv2.py` |
| **Genesis Block Integrity** | **100% PASS** | `python scripts/verify_genesis.py` |
| **P2P Wire Framing** | **100% PASS** | `python tests/test_p2p.py` |
| **Stratum V1 Pool Engine** | **100% PASS** | `python tests/test_functional_stratum.py` |
| **Mining & Subsidy** | **100% PASS** | `python tests/test_functional_mining.py` |
| **BIP39/44 Multi-Mode HD Wallet** | **100% PASS** | `python tests/test_functional_wallet.py` |
| **Full Mesh 3-Node P2P Relay** | **100% PASS** | `python tests/test_functional_p2p.py` |
| **10-Block Deep Reorganization** | **100% PASS** | `python tests/test_functional_reorg.py` |
| **Mempool Ingestion & Double-Spend Defense** | **100% PASS** | `python tests/test_multinode_stress.py` |
| **Zero-Leak Secret Scan** | **100% PASS** | `python scripts/verify_security.py` |

---

## 3. What is Experimental

- **C++ Dilithium Integration**: Experimental C++ research code in `src/crypto/dilithium/` is maintained for academic reference (`docs/security/AUDIT_REMEDIATION_VERIFICATION.md`). The active Layer-1 consensus engine uses the native C lattice library (`libqtydilithium`).
- **Compact Block Relay (BIP152)**: Full inventory/getdata block relay is authoritative; compact block filtering is slated for subsequent ecosystem phases.

---

## 4. What is Not Claimed

In adherence to Absolute Rules AR006 - AR010:
- **No Exaggerated TPS Claims**: We do not claim "thousands of transactions per second on live mainnet". Current measured mempool ingestion is 16 TX/sec on single-threaded test loops.
- **No "Instant Finality"**: QuantyCoin relies on Proof-of-Work probabilistic finality. Transactions confirm in mined blocks (60-second target interval).
- **No False Production Readiness**: Code components under active refactoring or audit are explicitly flagged.
- **No Fake Partnerships or Adoptions**: All ecosystem components in this repository represent genuine, self-contained open-source software.

---

## 5. How to Verify

Any engineer, node operator, or auditor can independently verify the protocol in under 3 minutes:

```bash
# 1. Clone repository
git clone https://github.com/timfromhcs/QuantyCoin.git
cd QuantyCoin

# 2. Run zero-leak security verification
python scripts/verify_security.py

# 3. Run core cryptographic and consensus tests
python tests/test_crypto.py
python tests/test_core.py

# 4. Run Stratum V1 mining pool integration test
python tests/test_functional_stratum.py

# 5. Run full automated integration test runner
python tests/test_runner.py

# 6. Run multi-node stress and hardness matrix
python tests/test_multinode_stress.py
```

Detailed verification instructions are available in [VERIFICATION.md](VERIFICATION.md).

---

## 6. How Releases are Created

1. **Source Freeze**: Code is frozen on a dedicated release branch with zero uncommitted changes.
2. **Security Gate**: `scripts/verify_security.py` verifies zero private keys, tokens, or vault paths are present.
3. **Test Gate**: All unit and functional tests must report 100% PASS.
4. **Reproducible Builds**: Packaged using native build scripts (`packaging/windows/`, `packaging/linux/`).
5. **Release Manifest**: Cryptographic SHA-256 checksums are generated and published alongside all release artifacts.

See [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for complete details.

---

## 7. Security Disclosures

Security vulnerabilities are handled confidentially with responsible disclosure guidelines:
- **Contact**: `timfromhcs@gmail.com`
- **Policy**: See [SECURITY.md](SECURITY.md) for response SLAs and vulnerability coordination.

---

## 8. Current Limitations

1. Python node performance is bounded by the Python interpreter; production high-density validating infrastructure will transition to native compiled kernels.
2. Full multi-thousand-node geographic peer discovery depends on DNS seed infrastructure and active community nodes.
