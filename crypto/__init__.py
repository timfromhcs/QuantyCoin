"""
QuantyCoin Cryptographic Engine Package
Zero-Mock Production Primitives
"""

from .hash import sha256, hash256, ripemd160, hash160, keccak256, compute_merkle_root
from .bip39 import generate_mnemonic, validate_mnemonic, mnemonic_to_seed, BIP39_WORDS
from .secp256k1 import (
    privkey_to_pubkey, ecdsa_sign, ecdsa_verify,
    encode_der_signature, decode_der_signature
)
from .bip32_44 import (
    HDKey, base58check_encode, base58check_decode,
    encode_segwit_address, bech32_encode, b58encode, b58decode,
    MAINNET_BECH32_HRP, MAINNET_PUBKEY_HASH_PREFIX
)
from .ed25519 import ed25519_public_key, ed25519_sign, ed25519_verify

__all__ = [
    "sha256", "hash256", "ripemd160", "hash160", "keccak256", "compute_merkle_root",
    "generate_mnemonic", "validate_mnemonic", "mnemonic_to_seed", "BIP39_WORDS",
    "privkey_to_pubkey", "ecdsa_sign", "ecdsa_verify", "encode_der_signature", "decode_der_signature",
    "HDKey", "base58check_encode", "base58check_decode", "encode_segwit_address", "bech32_encode",
    "b58encode", "b58decode", "MAINNET_BECH32_HRP", "MAINNET_PUBKEY_HASH_PREFIX",
    "ed25519_public_key", "ed25519_sign", "ed25519_verify"
]
