# QuantyCoin QTY4 Address Format Specification

**Protocol**: QTY4 (70040)  
**Encoding Schemes**: Bech32 (BIP173) & Bech32m (BIP350)  

---

## 1. Address Format Matrix

| Type | HRP | Witness Version | Checksum Spec | Prefix | Address Encoding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SegWit v0** | `qty` | `0` (`0x00`) | Bech32 | `qty1q` | 20-byte RIPEMD160(SHA256(pubkey)) | Classical ECDSA P2WPKH |
| **PQC v1** | `qty` | `1` (`0x51`) | Bech32m | `qty1p` | 32-byte SHA256(ML-DSA-44 pubkey) | Pure Post-Quantum P2WPKH |
| **Hybrid v2** | `qty` | `2` (`0x52`) | Bech32m | `qty1z` | 32-byte SHA256(ECDSA || ML-DSA) | Dual-Authorization Hybrid |

---

## 2. Testnet and Regtest Prefixes

- **Testnet**: HRP `tqty`
  - Mode 0: `tqty1q...`
  - Mode 1: `tqty1p...`
  - Mode 2: `tqty1z...`
- **Regtest**: HRP `rqty`
  - Mode 0: `rqty1q...`
  - Mode 1: `rqty1p...`
  - Mode 2: `rqty1z...`

---

## 3. Encoding & Decoding Rules

1. Mixed-case strings are strictly prohibited (addresses must be either entirely lowercase or uppercase).
2. For witness version 0, Bech32 checksum constant `1` must be used.
3. For witness versions 1 and 2, Bech32m checksum constant `0x2bc830a3` must be used.
4. The witness program must be between 2 and 40 bytes in length.
