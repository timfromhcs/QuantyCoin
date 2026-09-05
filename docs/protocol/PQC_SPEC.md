# QuantyCoin QTY4 Post-Quantum Cryptography Specification

**Protocol**: QTY4 (70040)  
**Standard**: NIST FIPS 204 (ML-DSA-44)  
**Implementation**: Native C Shared Library (`libqtydilithium`) with Python FFI  

---

## 1. Cryptographic Parameters

| Parameter | Standard Value | Description |
| :--- | :--- | :--- |
| **Algorithm** | ML-DSA-44 (Dilithium2) | NIST Security Category 2 (AES-128 equivalent) |
| **Public Key Size** | 1312 bytes | Serialized lattice polynomial vector $\mathbf{t}_1$ + $\rho$ |
| **Secret Key Size** | 2560 bytes | Polynomial vectors $\mathbf{s}_1, \mathbf{s}_2, \mathbf{K}, \text{tr}$ |
| **Signature Size** | 2420 bytes | Signature vector $(\mathbf{z}, \mathbf{h}, c)$ |
| **Seed Size** | 32 bytes | BIP32 HD expansion seed |
| **Fail-Closed Policy** | Enforced | Zero pseudo-crypto fallback tolerance |

---

## 2. Domain-Separated Sighash Digest

To prevent cross-protocol and cross-version signature replay attacks, all ML-DSA signatures bind to a domain-separated digest:

$$\text{DomainTag} = \text{"QUANTYCOIN\_QTY4\_PQC\_SIGHASH\_V1"}$$

$$\text{Commitment} = \text{SHA256}(\text{DomainTag} \parallel \text{chain\_id} \parallel \text{sighash\_type} \parallel \text{canonical\_tx\_digest})$$

Where:
- $\text{chain\_id} = \text{"quantycoin-4.0"}$
- $\text{sighash\_type}$ is the standard 1-byte sighash mode (`0x01` for `SIGHASH_ALL`).

---

## 3. Authorization Modes

1. **Mode 0 (`qty1q...`)**: Legacy ECDSA Secp256k1 (Witness v0). Maintained for historical compatibility.
2. **Mode 1 (`qty1p...`)**: Pure ML-DSA-44 Post-Quantum (Witness v1). 1312-byte public key and 2420-byte lattice signature.
3. **Mode 2 (`qty1z...`)**: Dual-Authorization Hybrid (Witness v2). Requires both a valid Secp256k1 signature and a valid ML-DSA-44 signature to spend.
