# QuantyCoin Protocol Specification: Quantum-Secure Mainnet Migration

**Document**: `MIGRATION_SPEC.md`  
**Protocol Layer**: Consensus Migration, State Transition & UTXO Lifecycle  
**Status**: **DRAFT SPECIFICATION — FROZEN FOR IMPLEMENTATION**  

---

## 1. Executive Summary & Security Philosophy

The arrival of a Cryptographically Relevant Quantum Computer (CRQC) capable of executing Shor's algorithm renders all classical discrete-logarithm and elliptic-curve cryptography (`secp256k1`) vulnerable to total private key recovery.

To protect user wealth without abruptly confiscating dormant classical coins, QuantyCoin establishes a phased four-stage migration model:
`LEGACY_CLASSICAL` &rarr; `TRANSITION` &rarr; `PQ_PREFERRED` &rarr; `PQ_REQUIRED`.

> **Fundamental Security Principle**: The network must **never** claim full quantum security as long as spendable classical-only UTXOs remain unrestricted on the ledger. Full quantum security is only achieved when the network reaches `PQ_REQUIRED`.

---

## 2. Four Phased Migration States

```
+------------------+     +------------------+     +------------------+     +------------------+
|      PHASE 1     |     |      PHASE 2     |     |      PHASE 3     |     |      PHASE 4     |
| LEGACY_CLASSICAL | --> |    TRANSITION    | --> |   PQ_PREFERRED   | --> |   PQ_REQUIRED    |
|                  |     |                  |     |                  |     |                  |
| Classical ECDSA  |     | PQC & Dual-PoW   |     | Mempool Priorit. |     | Classical Spends |
| Only             |     | Activated        |     | Higher Legacy Fee|     | Restricted/Sunset|
+------------------+     +------------------+     +------------------+     +------------------+
```

### 2.1 State 1: `LEGACY_CLASSICAL`
- Active up to the activation height $H_{\text{pqc\_activate}}$.
- Only classical Secp256k1 ECDSA (P2WPKH and P2PKH) transactions are recognized.
- Single-lane SHA-256D PoW.

### 2.2 State 2: `TRANSITION`
- **Activation**: Triggers at consensus block height $H_{\text{pqc\_activate}}$.
- **Consensus Capabilities**:
  - Dual Proof-of-Work lanes (`SHA256D_ASIC` and `GENERAL_PURPOSE`) are fully activated.
  - Post-quantum transaction verification is enabled:
    - Witness Version 1 (`ML_DSA-65`) and Witness Version 2 (`HYBRID`) are recognized as standard outputs.
    - Legacy P2WPKH and P2PKH outputs remain valid and spendable.
- **Wallet Behavior**: Default new address generation switches to `HYBRID` or `ML_DSA-65`. Wallets display migration banners guiding users to sweep classical balances into post-quantum custody.

### 2.3 State 3: `PQ_PREFERRED`
- **Activation**: Triggers at $H_{\text{pqc\_preferred}}$ (e.g. 1 year post-activation).
- **Mempool & Economic Incentives**:
  - PQC transactions receive standard mempool fee priority.
  - Legacy classical spends incur an additional witness validation fee to disincentivize long-term classical UTXO retention.
  - Miners prioritize PQC blocks to minimize exposure to unconfirmed classical transaction signatures in the mempool.

### 2.4 State 4: `PQ_REQUIRED` (Full Quantum Security)
- **Activation**: Triggers at $H_{\text{pqc\_required}}$ upon network-wide governance consensus or detected public quantum cryptanalysis breakthroughs.
- **Consensus Enforcement**:
  - Unmigrated classical P2PKH/P2WPKH outputs cannot be spent with pure ECDSA alone.
  - Spending legacy UTXOs requires an interactive migration proof or one-way proof-of-burn transition to a designated post-quantum address.
  - At this threshold, QuantyCoin formally achieves **100% Cryptographic Quantum Security**.

---

## 3. Wallet Migration UX & Address Conversion

To ensure seamless non-technical user transitions:
1. **Automated Balance Sweeper**:
   - Wallets provide a single-click `"Upgrade to Post-Quantum"` button.
   - Automatically gathers all classical UTXOs into a consolidated transaction paying directly to a newly derived `ML_DSA-65` address (`qty1p...`).
2. **Deterministic Derivation Path**:
   - Classical Secp256k1 keys: `m/44'/999'/account'/0/i`
   - Post-Quantum ML-DSA keys: Derived deterministically using domain-separated PBKDF2 / HKDF from the master BIP39 seed:
     $$\text{PQ\_Seed} = \text{HKDF-SHA512}(\text{BIP39\_Seed}, \text{salt}=\text{"QuantyCoin_ML_DSA_65"}, \text{info}=\text{account\_path})$$
   - Users do NOT need to record a second 24-word recovery phrase; their single BIP39 seed restores both classical and post-quantum keys.

---

## 4. Replay Protection & Fork Safety

To prevent signature replay between the legacy network and post-quantum branches:
1. All post-quantum sighash preimages mandate domain-separated headers (`"QUANTYCOIN_PQC_SIGHASH_V1"`).
2. Transaction version numbers for PQC transactions are bumped to $V \ge 2$.
3. Legacy nodes rejecting unknown witness programs treats them as standard `anyone-can-spend` under old rules unless coordinated via a defined activation block height.
