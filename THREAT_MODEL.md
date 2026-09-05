# QuantyCoin Formal Threat Model

**Protocol Version**: QTY4 (`70040`)  
**Security Architecture Standard**: Bounded Inputs, Hostile Network Assumption (R008), Consensus Invariance  

---

## 1. Security Philosophy & Assumptions

1. **Hostile Network Boundary**: Every peer connecting over TCP port 19444 is assumed malicious until verified. All inbound byte streams are validated against strict length limits and framing checksums.
2. **Deterministic Consensus**: Consensus rules are mathematically rigid. No wallet, RPC, mining, or GUI code is permitted to introduce divergence in block acceptance. Pure 64-bit integer arithmetic ensures identical results across architectures.
3. **Bounded Memory Consumption**: Deserialization routines enforce explicit byte caps (32 MB block limit) to prevent memory exhaustion attacks.

---

## 2. Attack Vectors & Defenses

### A. P2P Network Attacks

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Malformed Wire Packets** | Crash node or corrupt parser | Wire framing requires 4-byte magic (`0x51545934`), fixed length headers, and SHA256D checksum verification prior to parsing. | **VERIFIED** (`tests/test_adversarial_qty4.py`) |
| **Sybil & Peer Flooding** | Eclipse node connectivity | Maximum peer caps per IP; automatic disconnection of non-responsive peers; peer scoring system. | **VERIFIED** (`network/p2p_server.py`) |
| **Inventory / Orphan Storms** | Exhaust mempool or CPU | Unsolicited blocks without valid headers are rejected; mempool imposes maximum ancestor and size boundaries. | **VERIFIED** (`tests/test_multinode_stress.py`) |
| **Denial of Service (DoS)** | Socket exhaustion | Non-blocking socket polling with read timeouts; abrupt socket disconnection handled cleanly. | **VERIFIED** (`tests/test_multinode_stress.py`) |

### B. Consensus & Mining Attacks

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Invalid Proof-of-Work** | Poison chainstate | Strict comparison against compact target bits (`verify_pow()`); headers with insufficient work are dropped before transaction deserialization. | **VERIFIED** (`core/block.py`) |
| **Negative Target / Sign Bit Injection** | Artificially easy difficulty | Strict decoder checks `mantissa & 0x00800000 == 0`; rejects negative targets. | **VERIFIED** (`tests/test_adversarial_qty4.py`) |
| **Timestamp Manipulation** | Warp difficulty retargeting | Median Time Past (MTP) enforcement; blocks with timestamps in the past or > 2 hours in the future are rejected. | **VERIFIED** (`core/consensus.py`) |
| **Hashrate Hopping (Timewarp)** | Manipulate LWMA retarget | LWMA-1 retargets independently per-lane every block, clamping solve time to `[-6 * spacing, +6 * spacing]`. | **VERIFIED** (`core/consensus.py`) |
| **Low-Difficulty GPU Spam** | Reorganize canonical chain | Cumulative Thermodynamic Chainwork ($W_{\text{SHA256D}} = 1, W_{\text{Scrypt}} = 2048$); fork choice strictly follows total physical energy, defeating block-count inflation attacks. | **VERIFIED** (`tests/test_dualpow_security_simulation.py`) |
| **Double-Spending** | Replay or conflicting inputs | In-memory mempool conflict detection; UTXO database validates uniqueness of outpoints. | **VERIFIED** (`tests/test_multinode_stress.py`) |
| **Deep Reorg Partition** | Chain fork | Cumulative thermodynamic chainwork calculation; automatic rollback and state re-application on longer valid work. | **VERIFIED** (`tests/test_functional_reorg.py`) |

### C. Wallet & Cryptographic Attacks

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Quantum Cryptanalytic Attack (Shor's Algorithm)** | ECDSA key recovery | NIST FIPS 204 ML-DSA-44 lattice cryptography via native C acceleration (`libqtydilithium`); witness v1 (`qty1p...`) and v2 (`qty1z...`) addresses; sovereign UTXO migration tooling. | **VERIFIED** (`tests/test_pqc_dualpow_sv2.py`) |
| **Cross-Mode Signature Replay** | Replay classical signature in PQC mode | Domain-separated sighash: `SHA256("QUANTYCOIN_QTY4_PQC_SIGHASH_V1" \|\| sig_type \|\| BIP143_hash)` binding signatures uniquely to their authorization mode. | **VERIFIED** (`tests/test_pqc_dualpow_sv2.py`) |
| **Signature Malleability** | Alter TXID without invalidating sig | Strict DER validation for ECDSA; fixed-size lattice vectors for ML-DSA-44 (2,420 bytes); bit-flip rejection. | **VERIFIED** (`tests/test_adversarial_qty4.py`) |
| **Weak Entropy Key Generation** | Predictable private keys | Uses cryptographically secure `os.urandom(32)` for 24-word BIP39 seed generation. | **VERIFIED** (`crypto/bip39.py`) |
| **Secret Leakage to Disk/Git** | Private key exposure | Strict `.gitignore` policy and `scripts/verify_security.py` scanner. Genesis working files air-gapped in `QuantySecrets`. | **VERIFIED** (`scripts/verify_security.py`) |

---

## 3. Operational Security Guidelines

1. **RPC Surface**: RPC endpoints (port 19445) should remain bound to `127.0.0.1` unless protected by secure tunnels or reverse proxies with authentication.
2. **Fail-Closed Consensus**: The node strictly terminates via `CryptographicBackendUnavailableError` if native lattice acceleration is unavailable, preventing fallback to unverified pseudo-cryptography.
