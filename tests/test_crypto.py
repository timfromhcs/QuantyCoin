"""
QuantyCoin Unit Test - Cryptography Engine Verification
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto import (
    generate_mnemonic, validate_mnemonic, mnemonic_to_seed,
    HDKey, ecdsa_sign, ecdsa_verify, privkey_to_pubkey,
    hash256, ed25519_public_key, ed25519_sign, ed25519_verify
)


def test_crypto_pipeline():
    # 1. BIP39 Mnemonic
    mnemonic = generate_mnemonic(256)
    assert validate_mnemonic(mnemonic), "Mnemonic validation failed"
    words = mnemonic.split()
    assert len(words) == 24, f"Expected 24 words, got {len(words)}"
    
    # 2. HD Key Derivation (BIP44)
    seed = mnemonic_to_seed(mnemonic)
    master = HDKey.from_seed(seed)
    creator_key = master.derive_path("m/44'/999'/0'/0/0")
    wif = creator_key.to_wif()
    addr = creator_key.get_address()
    pub = creator_key.get_public_key()
    assert addr.startswith("qty1q"), f"Address should start with qty1q, got {addr}"
    
    # 3. Secp256k1 ECDSA
    msg_hash = hash256(b"QuantyCoin Layer 1 Test")
    r, s = ecdsa_sign(msg_hash, creator_key.key)
    verified = ecdsa_verify(msg_hash, pub, r, s)
    assert verified, "ECDSA verification failed"
    
    # 4. Ed25519
    ed_sk = creator_key.key
    ed_pk = ed25519_public_key(ed_sk)
    ed_sig = ed25519_sign(b"Quantum Payload", ed_sk, ed_pk)
    ed_verified = ed25519_verify(ed_sig, b"Quantum Payload", ed_pk)
    assert ed_verified, "Ed25519 verification failed"
    
    print("Crypto Pipeline Verification: 100% PASS")
    print(f"Sample Address: {addr}")
    print(f"WIF: {wif[:10]}...{wif[-5:]}")


if __name__ == "__main__":
    test_crypto_pipeline()
