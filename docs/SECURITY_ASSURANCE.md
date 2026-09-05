# QuantyCoin Security Assurance & Proof of Isolation

**Protocol Version**: QTY4 (`70040`)  
**Network Identity**: `quantycoin-4.0`  
**Security Standard**: Air-Gapped Secret Isolation, Hostile Network Assumption (R008), Fail-Closed Cryptography  

---

## 1. Zero-Secret Repository Guarantee

### A. Air-Gapped Vault Architecture
QuantyCoin strictly mandates that no private cryptographic keys, generator seeds, raw nonce search logs, or release signing credentials may ever enter the Git working tree. All private artifacts reside in an external, non-tracked directory:
- **Windows**: `%USERPROFILE%\Desktop\QuantyVault\QuantyCoin`
- **Linux/macOS**: `~/Desktop/QuantyVault/QuantyCoin`

Vault Subdirectories:
- `genesis/working/`: Candidate generation seeds and scratch nonce search outputs
- `genesis/generated/`: Initial candidate block structures
- `genesis/verification/`: Dual-path independent cross-verification outputs
- `genesis/archive/`: Immutable historical logs
- `signing/`: Release GPG/code-signing keys
- `release/`: Final signed checksums and installers
- `manifests/`: Audit and verification manifests

### B. Automated Secret Scanner
The repository incorporates [`scripts/verify_security.py`](../scripts/verify_security.py), which is executed in pre-commit hooks and CI pipelines. The scanner inspects every file in the repository tree against:
- Private key patterns (`BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY`)
- BIP39 recovery seed phrases
- Known test secret values and vault paths
- Forbidden file extensions (`.pem`, `.key`, `.pfx`, `.secret`, `.wallet`)
- Result: **0 SECRETS DETECTED (100% CLEAN)**.

---

## 2. Post-Quantum Lattice Security (NIST FIPS 204 ML-DSA-44)

QuantyCoin implements post-quantum digital signature authorization using ML-DSA-44 (CRYSTALS-Dilithium2):
1. **Zero Mock Fallback**: The node never falls back to pseudo-cryptography. If native C lattice acceleration (`libqtydilithium`) is unavailable, `CryptographicBackendUnavailableError` is raised immediately.
2. **Fixed-Size Validation**:
   - Public keys must be exactly 1,312 bytes.
   - Signatures must be exactly 2,420 bytes.
   - Any malformed, truncated, or padded key/signature is immediately rejected.
3. **Domain Separation**:
   - Every PQC signature signs a domain-separated digest:
     $$\text{Digest} = \text{SHA256}(\mathtt{b"QUANTYCOIN\_QTY4\_PQC\_SIGHASH\_V1"} \mathbin{\Vert} \text{SigType} \mathbin{\Vert} \text{BIP143Sighash})$$
   - This prevents cross-protocol and cross-mode signature replay.

---

## 3. Hostile Network Boundary & DoS Mitigations

Under Rule R008 (**NETWORK_INPUT_IS_HOSTILE**), all external input arriving from peers or RPC clients is treated as untrusted:
- **Wire Framing**: 24-byte header (`Magic 0x51545934`, Command 12-char, Length uint32_le, Checksum uint32_le). Messages with invalid magic or checksum mismatches are dropped immediately before memory allocation.
- **Payload Size Caps**: Maximum wire payload is strictly capped at 32 MB (`33,554,432` bytes).
- **Socket Timeouts**: Non-blocking asynchronous I/O prevents slow-loris socket exhaustion.
- **Mempool Ancestor Limits**: Strict ancestor and descendant count limits prevent memory exhaustion via transaction chains.

---

## 4. Adversarial Verification Suite

The dedicated adversarial test suite [`tests/test_adversarial_qty4.py`](../tests/test_adversarial_qty4.py) confirms that all attack vectors are rejected cleanly:

| Attack Vector | Test Method | Result | Defense Mechanism |
| :--- | :--- | :---: | :--- |
| **Negative Compact Target** | `test_compact_target_decoder_adversarial_rejections` | **REJECTED** | Sign bit `0x00800000` check |
| **Target Exponent Overflow** | `test_compact_target_decoder_adversarial_rejections` | **REJECTED** | Exponent bound check (`<= 34`) |
| **Header Fuzzing** | `test_block_header_fuzz_deserialization` | **REJECTED** | Fixed 80-byte header length validation |
| **Malformed Transaction** | `test_malformed_transaction_wire_fuzzing` | **REJECTED** | Bounds-checked VarInt and byte parsers |
| **PQC Bit-Flip Malleability**| `test_pqc_signature_bitflip_rejections` | **REJECTED** | Deterministic lattice verification |
| **PQC Key Truncation** | `test_pqc_key_length_enforcement` | **REJECTED** | Exact 1312-byte key size assertion |
| **Hybrid Signature Bypass** | `test_hybrid_witness_tamper_rejection` | **REJECTED** | Dual-signature requirement |
| **P2P Wire Magic Corrupt** | `test_p2p_wire_framing_corruptions` | **REJECTED** | Magic `0x51545934` assertion |
| **P2P Length Overflow** | `test_p2p_wire_framing_corruptions` | **REJECTED** | Maximum message size threshold |
| **Stratum V2 Magic Tamper** | `test_stratum_v2_frame_corruption` | **REJECTED** | Framing validator |
| **Corrupted Address** | `test_address_encoding_corruptions` | **REJECTED** | Bech32 checksum verification |
| **UTXO Non-Mutation** | `test_utxo_non_mutation_on_invalid_block` | **VERIFIED** | Atomic state rollback on error |
| **Atomic Deep Reorg** | `test_chainstate_atomic_reorg_rollback` | **VERIFIED** | Undo log rollback guarantee |
