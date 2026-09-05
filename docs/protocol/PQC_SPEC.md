# QuantyCoin Protocol Specification: Post-Quantum Cryptography (PQC)

**Document**: `PQC_SPEC.md`  
**Protocol Layer**: Layer-1 Transaction Authorization & Cryptographic Signatures  
**Standard Reference**: NIST FIPS 204 (Module-Lattice-Based Digital Signature Standard / ML-DSA)  
**Status**: **DRAFT SPECIFICATION — FROZEN FOR IMPLEMENTATION**  

---

## 1. Scope & Architectural Goals

The goal of this specification is to establish a standardized, deterministic post-quantum transaction authorization subsystem for QuantyCoin, securing user funds against future Cryptographically Relevant Quantum Computers (CRQCs) while preserving backward compatibility during the network transition window.

---

## 2. Cryptographic Algorithm Evaluation & Selection

### 2.1 NIST FIPS 204 Parameter Sets Comparison

| Metric | ML-DSA-44 (Category 2) | ML-DSA-65 (Category 3) | ML-DSA-87 (Category 5) |
| :--- | :--- | :--- | :--- |
| **NIST Security Level** | Equivalent to AES-128 | Equivalent to AES-192 | Equivalent to AES-256 |
| **Public Key Size** | 1,312 bytes | **1,952 bytes** | 2,592 bytes |
| **Signature Size** | 2,420 bytes | **3,309 bytes** | 4,627 bytes |
| **Verification Speed** | Fast (~0.12 ms) | **Balanced (~0.18 ms)** | Moderate (~0.28 ms) |
| **Signing Speed** | Fast (~0.35 ms) | **Balanced (~0.55 ms)** | Moderate (~0.85 ms) |
| **Single-Input Tx Size** | ~3.8 KB | **~5.4 KB** | ~7.3 KB |
| **Block Impact (at 1000 tx)**| ~3.8 MB | **~5.4 MB** | ~7.3 MB |

### 2.2 Selection Decision
- **Primary Standard**: **ML-DSA-44** (NIST Category 2 / CRYSTALS-Dilithium2) is selected as the default production post-quantum digital signature algorithm.
- **Rationale**: ML-DSA-44 provides NIST Category 2 quantum security margin (equivalent to AES-128 against quantum cryptanalysis) while maintaining a compact 1,312-byte public key and 2,420-byte signature. It offers ultra-fast verification (~0.12 ms) and signing (~0.35 ms) on consumer hardware, preserving rapid block verification throughput and accessible transaction fees on Layer-1.

---

## 3. Cryptographic Signature Types

QuantyCoin transactions support three explicit signature schemes:

```
enum SignatureType : uint8_t {
    LEGACY_ECDSA = 0x00,  // Standard Secp256k1 ECDSA (RFC 6979)
    HYBRID       = 0x01,  // Dual Secp256k1 ECDSA + NIST FIPS 204 ML-DSA-44
    ML_DSA       = 0x02   // Pure NIST FIPS 204 ML-DSA-44
}
```

### 3.1 Mode 0: `LEGACY_ECDSA`
- Classical 256-bit Secp256k1 elliptic curve cryptography.
- Public key: 33 bytes compressed.
- Signature: 71–73 bytes DER + 1 byte sighash type.
- Retained for legacy UTXO compatibility and lightweight hardware wallet devices.

### 3.2 Mode 1: `HYBRID` (Defense-in-Depth)
- Requires both a classical Secp256k1 signature and an ML-DSA-44 signature.
- **Security Invariant**: Compromising the transaction requires breaking *both* the discrete logarithm problem on Secp256k1 *and* the Short Integer Solution / Learning With Errors lattice problem in ML-DSA.
- Witness Stack:
  1. `ecdsa_signature` (DER + sighash byte)
  2. `ecdsa_pubkey` (33 bytes)
  3. `mldsa_signature` (2,420 bytes + 1 byte sighash type)
  4. `mldsa_pubkey` (1,312 bytes)

### 3.3 Mode 2: `ML_DSA` (Pure Quantum-Secure)
- Direct post-quantum authorization.
- Witness Stack:
  1. `mldsa_signature` (2,420 bytes + 1 byte sighash type)
  2. `mldsa_pubkey` (1,312 bytes)

---

## 4. Address Encoding & Witness Programs

### 4.1 Native Post-Quantum Witness Program (Bech32m)
All post-quantum addresses utilize BIP 350 Bech32m with Human Readable Part `qty` (Mainnet), `tqty` (Testnet), or `rqty` (Regtest).

- **Witness Version 1 (Pure ML-DSA-44)**:
  - ScriptPubKey: `0x51 0x20 <32-byte-hash>` (`OP_1 PUSH32 <hash>`)
  - The 32-byte hash is:
    $$\text{pqc\_program} = \text{SHA256}(\text{ML-DSA-44 PubKey})$$
  - Address prefix: `qty1p...` (Bech32m encoded).

- **Witness Version 2 (Hybrid ECDSA + ML-DSA-44)**:
  - ScriptPubKey: `0x52 0x20 <32-byte-hash>` (`OP_2 PUSH32 <hash>`)
  - The 32-byte hash is:
    $$\text{hybrid\_program} = \text{SHA256}(\text{Secp256k1 PubKey} \parallel \text{ML-DSA-44 PubKey})$$
  - Address prefix: `qty1z...` (Bech32m encoded).

---

## 5. Domain-Separated Sighash Calculation

To prevent cross-protocol, cross-mode, and cross-chain replay attacks, the sighash preimage for post-quantum inputs incorporates explicit domain separation:

$$\text{Domain Tag} = \text{"QUANTYCOIN_PQC_SIGHASH_V1"}$$

$$\text{PQC\_Sighash} = \text{SHA256}(\text{Domain Tag} \parallel \text{SigType} \parallel \text{BIP143\_Preimage})$$

Where:
- `SigType`: `0x01` for HYBRID, `0x02` for ML_DSA.
- `BIP143_Preimage`: Serialized transaction inputs, outputs, amounts, sequences, and locktime according to BIP 143.

---

## 6. Transaction Weight & Fee Accounting

Because ML-DSA public keys and signatures are substantially larger than classical ECC keys, QuantyCoin applies SegWit discount accounting to witness data:

$$\text{Base Size} = \text{len}(\text{tx.serialize}(\text{include\_witness}=\text{False}))$$
$$\text{Total Size} = \text{len}(\text{tx.serialize}(\text{include\_witness}=\text{True}))$$
$$\text{Witness Size} = \text{Total Size} - \text{Base Size}$$
$$\text{Weight} = (\text{Base Size} \times 3) + \text{Total Size} = (\text{Base Size} \times 4) + \text{Witness Size}$$
$$\text{Virtual Size (vsize)} = \left\lceil \frac{\text{Weight}}{4} \right\rceil$$

For an ML-DSA-44 transaction (~3,732 bytes of witness), the virtual size is approximately 1,050 vB. At a minimum relay fee of 1 sat/vB, an ML-DSA transaction pays ~1,050 Satoshis (~0.00001050 QTY), preserving accessible network fees while accurately accounting for node memory and disk usage.

