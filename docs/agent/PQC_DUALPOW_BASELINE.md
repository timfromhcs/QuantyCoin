# QuantyCoin 2.0 (QTY2) Current State Baseline Audit: PQC, Dual-PoW & Stratum V2

**Contract ID**: `QUANTYCOIN-QTY2-PQC-DUALPOW-SV2-2026`  
**Protocol Version**: QTY2 (Protocol 70020)  
**Date**: September 2026  
**Auditor**: Autonomous Protocol Rebuild Agent  
**Scope**: Cryptographic Signatures, Transaction Format, Address Formats, PoW & Retargeting, Chainwork Engine, Mining & Stratum Architecture, C++ Dilithium Experiment, and Migration Risks.

---

## 1. Executive Summary

This audit establishes the definitive technical baseline of QuantyCoin QTY2 prior to introducing Post-Quantum Cryptography (NIST FIPS 204 ML-DSA), Dual Proof-of-Work mining lanes (SHA-256D ASIC + General-Purpose CPU/GPU), and Stratum V2 protocol support.

The operational blockchain stack in Python (`core/`, `crypto/`, `network/`, `node/`, `wallet/`, `miner/`, `ui/`) is currently locked to single-lane SHA-256D PoW and classical Secp256k1 ECDSA (P2WPKH / P2PKH) signatures. The C++ tree (`src/`) contains an experimental, unactivated prototype of CRYSTALS-Dilithium signature integration.

---

## 2. Current Signature Model

### Classical Cryptography Stack
- **Elliptic Curve**: `secp256k1` ($y^2 = x^3 + 7 \pmod p$), implemented in `crypto/secp256k1.py`.
- **Signature Algorithm**: ECDSA with RFC 6979 deterministic nonce generation $k = \text{HMAC-SHA256}(d, m)$.
- **Signature Encoding**: Standard ASN.1 DER encoding (`encode_der_signature(r, s)`) appended with a single sighash flag byte (`0x01` = `SIGHASH_ALL`), yielding signatures between 71 and 73 bytes.
- **Key Sizes**:
  - Private Key: 32 bytes (256 bits).
  - Public Key: 33 bytes compressed (prefixed with `0x02` or `0x03`). Uncompressed 65-byte public keys are supported in low-level primitives but deprecated in modern address derivation.
- **Verification Routine**: `core/transaction.py:verify_input_signature()` expects `inp.witness` to consist of `[der_sig, pubkey]`.
- **Limitations**: Completely vulnerable to Shor's algorithm on a cryptographically relevant quantum computer (CRQC). Discrete logarithm can be computed in polynomial time $O((\log p)^3)$.

---

## 3. Current Transaction Format & Witness Rules

### Serialization Architecture (`core/transaction.py`)
- **Version**: 4-byte little-endian signed integer (`version = 1`).
- **SegWit Flag**: BIP 141 marker `0x00` and flag `0x01` if any input contains non-empty witness items.
- **Input Structure (`TxIn`)**:
  - `prev_txid`: 32 bytes little-endian.
  - `prev_vout`: 4 bytes unsigned int.
  - `script_sig`: VarInt length + bytes (empty `b''` for Native SegWit P2WPKH).
  - `sequence`: 4 bytes unsigned int (`0xFFFFFFFF`).
  - `witness`: VarInt count of items, each preceded by VarInt length.
- **Output Structure (`TxOut`)**:
  - `value`: 8 bytes unsigned int (Satoshis, $10^8$ per QTY).
  - `script_pubkey`: VarInt length + script bytes.
- **Locktime**: 4 bytes unsigned int.
- **Sighash Algorithm**: BIP 143 double-SHA256 preimage:
  $$\text{hash256}(\text{version} \parallel \text{hashPrevouts} \parallel \text{hashSequence} \parallel \text{outpoint} \parallel \text{scriptCode} \parallel \text{amount} \parallel \text{sequence} \parallel \text{hashOutputs} \parallel \text{locktime} \parallel \text{sighashType})$$
- **Transaction Identifiers**:
  - `txid`: Double-SHA256 of transaction serialized *without* witness marker, flag, or witness arrays.
  - `wtxid`: Double-SHA256 of full transaction serialization including witness.

---

## 4. Current Address Model

- **Native SegWit (P2WPKH)**:
  - Human Readable Part (HRP): `qty` (Mainnet), `tqty` (Testnet), `rqty` (Regtest).
  - Witness Version: `0` (`0x00`).
  - Witness Program: 20-byte `hash160(compressed_pubkey)` (`RIPEMD160(SHA256(pubkey))`).
  - ScriptPubKey: `0x00 0x14 <20-byte witness program>` (22 bytes total).
  - Format: Bech32 checksummed string (`qty1q...`).
- **Legacy Base58Check (P2PKH)**:
  - Version Byte: `0x3A` (58 decimal), yielding leading `'Q'` prefix.
  - Payload: 20-byte `hash160(pubkey)` + 4-byte double-SHA256 checksum.
  - ScriptPubKey: `OP_DUP OP_HASH160 0x14 <hash> OP_EQUALVERIFY OP_CHECKSIG` (25 bytes total).

---

## 5. Current Proof-of-Work Model

### Header Specification (`core/block.py`)
- Standard 80-byte header:
  - `version`: 4 bytes int32 (`0x01`).
  - `prev_block`: 32 bytes little-endian.
  - `merkle_root`: 32 bytes little-endian.
  - `timestamp`: 4 bytes uint32.
  - `bits`: 4 bytes uint32 compact difficulty target.
  - `nonce`: 4 bytes uint32.
- **PoW Function**: Double-SHA256:
  $$\text{PoW}(H) = \text{SHA256}(\text{SHA256}(H))$$
- **Target Comparison**:
  $$\text{int.from\_bytes}(\text{PoW}(H)[::-1], \text{'big'}) \le \text{bits\_to\_target}(H.\text{bits})$$
- **Single-Lane Constraint**: Currently, only SHA-256D is recognized. The header does not have an explicit lane identifier field; `version` is not lane-differentiated.

---

## 6. Current Difficulty Adjustment Model (LWMA-1)

### Algorithm (`core/consensus.py`)
- **Type**: Linear-Weighted Moving Average (LWMA-1).
- **Window**: $N = 45$ blocks.
- **Formula**:
  $$\text{solve\_time}_i = \text{clamp}(T_i - T_{i-1}, -6 \cdot S, 6 \cdot S)$$
  $$W = \frac{N(N + 1)}{2} = \sum_{i=1}^{N} i$$
  $$t = \sum_{i=1}^{N} (\text{solve\_time}_i \cdot i)$$
  $$\text{avg\_target} = \frac{1}{N} \sum_{i=1}^{N} \text{target}_i$$
  $$\text{next\_target} = \frac{\text{avg\_target} \cdot t}{S \cdot W}$$
- **Parameters**: Target spacing $S = 60$ seconds, max clamp $360$ seconds.
- **Limit**: Bounded above by `POW_LIMIT_TARGET` (`0x00000fffff...`, bits `0x1e0fffff`).
- **Limitation**: Only tracks a single historical target series. Does not differentiate between hardware classes or separate mining lanes.

---

## 7. Current Chainwork Model

### Formula (`node/chainstate.py`)
$$\text{work}(B) = \left\lfloor \frac{2^{256}}{\text{target}(B) + 1} \right\rfloor$$
$$\text{chainwork}(T) = \sum_{B \in \text{Chain}(T)} \text{work}(B)$$
- **Fork Choice Rule**:
  $$\text{Best Tip} = \arg\max_{T} (\text{chainwork}(T))$$
- **Limitation**: In a dual-PoW context, if a secondary lane operates at much lower raw difficulty without lane-specific normalization or weight adjustment, an attacker could either game the difficulty window or skew chain progression if work calculations are unweighted.

---

## 8. Current Mining Architecture & Stratum V1

### Solo & Engine (`miner/engine.py`)
- Multi-threaded Python worker searching 32-bit nonce space with strided offsets.
- Interacts via JSON-RPC `getblocktemplate` and `submitblock`.

### Stratum V1 Server (`miner/stratum.py`)
- TCP server on port `3333`.
- Methods implemented:
  - `mining.subscribe`: Issues `ExtraNonce1` (4 bytes hex) and `ExtraNonce2_size` (4 bytes).
  - `mining.authorize`: Validates miner worker login.
  - `mining.submit`: Receives `[worker_name, job_id, extranonce2, ntime, nonce]`, validates share, updates metrics.
  - `mining.set_difficulty`: Notifies connected miners of pool share target.
- **Limitations**:
  - Plaintext JSON lines over TCP; no native encryption.
  - High bandwidth overhead due to JSON parsing.
  - No binary framing, no channel multiplexing, no miner-negotiated block templates.

---

## 9. Current C++ Post-Quantum Experiment (`src/`)

### Codebase Inspection
- Fork of Bitcoin Knots reference containing CRYSTALS-Dilithium code under `src/crypto/dilithium/`.
- Wrapper: `src/crypto/dilithium_wrapper.c`, `src/crypto/dilithium_key.cpp`.
- Mode evaluated in C++: Dilithium Level 3 / Level 5 prototypes (round 3 NIST submission, predecessor to FIPS 204 ML-DSA).
- Descriptors: `src/script/dilithium_signing_provider.cpp` evaluating `p2mr` (Pay-to-Merkle-Root) script trees.
- **Status in Active Network**: Completely dormant. The Python engine is the active consensus node. None of the C++ Dilithium logic is active on mainnet consensus.

---

## 10. Exact Migration Risks & Challenges

1. **Signature Size Explosion**:
   - Classical ECDSA signature: ~72 bytes.
   - ML-DSA-44: Public key 1,312 bytes, signature 2,420 bytes (~2.4 KB).
   - ML-DSA-65: Public key 1,952 bytes, signature 3,309 bytes (~3.3 KB).
   - ML-DSA-87: Public key 2,592 bytes, signature 4,627 bytes (~4.6 KB).
   - *Risk*: A single ML-DSA transaction consumes ~5 KB vs ~250 bytes for P2WPKH (20x increase). Block size and mempool limits must account for witness weight.
2. **Backward Compatibility vs Network Fork**:
   - Adding a new signature scheme and a new PoW lane to an existing blockchain requires either a soft-fork (via witness extensions) or a hard-fork / new protocol activation.
   - If old nodes cannot parse the new block header or witness format, an uncoordinated activation causes a permanent chain split.
3. **Dual-PoW 51% & Game-Theoretic Attacks**:
   - If General-Purpose (CPU/GPU) difficulty is low and shares block production 50/50 with SHA-256D without decoupled chainwork and independent retargeting, an attacker with rented GPU/cloud capacity could orphan ASIC blocks or manipulate difficulty.
   - Retargeting must be decoupled: SHA-256D miners adjust against SHA-256D block intervals; General-Purpose miners adjust against General-Purpose block intervals.
4. **UTXO Quantum Vulnerability Window**:
   - Classical UTXOs whose public keys have been revealed on-chain (e.g. from prior spends or address reuse) are immediately vulnerable to a CRQC.
   - Unspent P2WPKH outputs where only the 20-byte hash is published remain pre-image protected until spent, but are vulnerable during the mempool broadcast window.
   - Transition states (`LEGACY_CLASSICAL`, `TRANSITION`, `PQ_PREFERRED`, `PQ_REQUIRED`) must be formally defined.
