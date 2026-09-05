# QuantyCoin Trust Center

**Last Updated**: 2026-09-05  
**Protocol Version**: QTY2 (`70020`)  
**Core Policy**: Verification Over Marketing  

---

## 1. What is QuantyCoin?

QuantyCoin (QTY) is an independent, open-source Layer-1 cryptocurrency combining authoritative SHA-256D Proof-of-Work mining, rapid 60-second block intervals, responsive LWMA-1 difficulty retargeting, 32 MB block capacity, native Stratum V1 mining pool architecture, BIP39/44 HD wallets with Bech32 native witness addresses, and a multi-node P2P gossip network.

---

## 2. What is Verified

The following components are implemented, tested, and verifiably reproducible directly from this repository:

| Subsystem | Verified State | Test / Verification Command |
| :--- | :--- | :--- |
| **SHA-256D Consensus** | **100% PASS** | `python tests/test_core.py` |
| **Genesis Block Integrity** | **100% PASS** | Runtime assertion in `node/chainstate.py` matching `genesis/PUBLIC_GENESIS_MANIFEST.json` |
| **P2P Wire Framing** | **100% PASS** | `python tests/test_p2p.py` |
| **Stratum V1 Pool Engine** | **100% PASS** | `python tests/test_functional_stratum.py` |
| **Mining & Subsidy** | **100% PASS** | `python tests/test_functional_mining.py` |
| **BIP39/44 HD Wallet & Tx Signing** | **100% PASS** | `python tests/test_functional_wallet.py` |
| **Full Mesh 3-Node P2P Relay** | **100% PASS** | `python tests/test_functional_p2p.py` |
| **10-Block Deep Reorganization** | **100% PASS** | `python tests/test_functional_reorg.py` |
| **Mempool Ingestion & Double-Spend Defense** | **100% PASS** | `python tests/test_multinode_stress.py` |
| **Zero-Leak Secret Scan** | **100% PASS** | `python scripts/verify_security.py` |

---

## 3. What is Experimental

- **C++ Dilithium Integration**: Post-quantum signature integration in the C++ reference tree (`src/crypto/dilithium/`) is in active research and audit remediation (`docs/security/AUDIT_REMEDIATION_VERIFICATION.md`). The active Python Layer-1 baseline currently utilizes classical Secp256k1 ECDSA.
- **Stratum V2 Protocol**: Stratum V1 is fully verified; Stratum V2 is preserved as an architectural extension point.
- **Compact Block Relay (BIP152)**: Full inventory/getdata block relay is authoritative; compact blocks are slated for post-stabilization activation.

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
4. **Reproducible Builds**: Packaged using native build scripts (`packaging/windows/`, `packaging/linux/`, `packaging/macos/`).
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
