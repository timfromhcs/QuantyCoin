# QuantyCoin Formal Threat Model

**Protocol Version**: QTY2 (`70020`)  
**Security Architecture Standard**: Bounded Inputs, Hostile Network Assumption (R008), Consensus Invariance  

---

## 1. Security Philosophy & Assumptions

1. **Hostile Network Boundary**: Every peer connecting over TCP port 19888 is assumed malicious until verified. All inbound byte streams are validated against strict length limits and framing checksums.
2. **Deterministic Consensus**: Consensus rules are mathematically rigid. No wallet, RPC, mining, or GUI code is permitted to introduce divergence in block acceptance.
3. **Bounded Memory Consumption**: Deserialization routines enforce explicit byte caps to prevent memory exhaustion attacks.

---

## 2. Attack Vectors & Defenses

### A. P2P Network Attacks

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Malformed Wire Packets** | Crash node or corrupt parser | Wire framing requires 4-byte magic (`0x5155414E`), fixed length headers, and SHA256D checksum verification prior to parsing. | **VERIFIED** (`tests/test_p2p.py`) |
| **Sybil & Peer Flooding** | Eclipse node connectivity | Maximum peer caps per IP; automatic disconnection of non-responsive peers; peer scoring system. | **VERIFIED** (`network/p2p_server.py`) |
| **Inventory / Orphan Storms** | Exhaust mempool or CPU | Unsolicited blocks without valid headers are rejected; mempool imposes maximum ancestor and size boundaries. | **VERIFIED** (`tests/test_multinode_stress.py`) |
| **Denial of Service (DoS)** | Socket exhaustion | Non-blocking socket polling with read timeouts; abrupt socket disconnection handled cleanly. | **VERIFIED** (`tests/test_multinode_stress.py`) |

### B. Consensus & Mining Attacks

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Invalid Proof-of-Work** | Poison chainstate | Strict comparison against compact target bits (`verify_pow()`); headers with insufficient work are dropped before transaction deserialization. | **VERIFIED** (`core/block.py`) |
| **Timestamp Manipulation** | Warp difficulty retargeting | Median Time Past (MTP) enforcement; blocks with timestamps in the past or > 2 hours in the future are rejected. | **VERIFIED** (`core/consensus.py`) |
| **Hashrate Hopping (Timewarp)** | Manipulate LWMA retarget | LWMA-1 retargets every single block, clamping solve time to `[-6 * spacing, +6 * spacing]`. | **VERIFIED** (`core/consensus.py`) |
| **Double-Spending** | Replay or conflicting inputs | In-memory mempool conflict detection; UTXO database validates uniqueness of outpoints. | **VERIFIED** (`tests/test_multinode_stress.py`) |
| **Deep Reorg Partition** | Chain fork | Cumulative chainwork calculation (`1 << 256 / (target + 1)`); automatic rollback and state re-application on longer valid work. | **VERIFIED** (`tests/test_functional_reorg.py`) |

### C. Wallet & Key Storage

| Threat | Impact | Mitigation Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| **Weak Entropy Key Generation** | Predictable private keys | Uses cryptographically secure `os.urandom(32)` for 24-word BIP39 seed generation. | **VERIFIED** (`crypto/bip39.py`) |
| **Secret Leakage to Disk/Git** | Private key exposure | Strict `.gitignore` policy and `scripts/verify_security.py` scanner. Genesis working files air-gapped in `QuantySecrets`. | **VERIFIED** (`scripts/verify_security.py`) |
| **Transaction Signature Forgery** | Fund theft | RFC 6979 deterministic ECDSA signing; strict DER decoding and public key validation. | **VERIFIED** (`tests/test_crypto.py`) |

---

## 3. Residual Risks & In-Progress Areas

1. **Post-Quantum Dilithium C++ Layer**: The C++ Dilithium integration in `src/` requires completion of audit remediations before mainnet activation.
2. **RPC Surface**: RPC endpoints should remain bound to `127.0.0.1` unless protected by secure tunnels or reverse proxies with authentication.
