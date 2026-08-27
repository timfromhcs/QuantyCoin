"""
QuantyCoin Core Cryptography - Secp256k1 Elliptic Curve Engine
Pure Python Mathematical Implementation (Zero External C-Dependencies, RFC 6979 Deterministic Nonce)
100% Zero-Mock & Bit-Exact with Bitcoin/QuantyCoin Standard
"""

import hashlib
import hmac
from typing import Tuple, Optional

# Secp256k1 Curve Constants
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_A = 0
_B = 7
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_G = (_Gx, _Gy)
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def _mod_inverse(a: int, m: int = _P) -> int:
    """Compute modular inverse using Extended Euclidean Algorithm."""
    if a < 0:
        a = (a % m + m) % m
    prev_r, r = a, m
    prev_x, x = 1, 0
    while r != 0:
        q = prev_r // r
        prev_r, r = r, prev_r - q * r
        prev_x, x = x, prev_x - q * x
    return (prev_x % m + m) % m


def _point_add(p1: Optional[Tuple[int, int]], p2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    """Elliptic curve point addition on Secp256k1."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    
    if x1 == x2:
        if y1 != y2:
            return None # Point at infinity
        # Point doubling
        lam = (3 * x1 * x1 + _A) * _mod_inverse(2 * y1, _P) % _P
    else:
        lam = (y2 - y1) * _mod_inverse(x2 - x1, _P) % _P
        
    x3 = (lam * lam - x1 - x2) % _P
    y3 = (lam * (x1 - x3) - y1) % _P
    return (x3, y3)


def _point_mul(k: int, p: Tuple[int, int] = _G) -> Optional[Tuple[int, int]]:
    """Elliptic curve scalar multiplication (double-and-add)."""
    k = k % _N
    if k == 0:
        return None
    res = None
    addend = p
    while k > 0:
        if k & 1:
            res = _point_add(res, addend)
        addend = _point_add(addend, addend)
        k >>= 1
    return res


def privkey_to_pubkey(privkey_bytes: bytes, compressed: bool = True) -> bytes:
    """Derive Secp256k1 public key bytes from 32-byte private key."""
    if len(privkey_bytes) != 32:
        raise ValueError("Private key must be exactly 32 bytes")
    priv_num = int.from_bytes(privkey_bytes, 'big')
    if priv_num <= 0 or priv_num >= _N:
        raise ValueError("Private key scalar out of valid range (1 .. N-1)")
        
    pt = _point_mul(priv_num, _G)
    assert pt is not None
    x, y = pt
    
    if compressed:
        prefix = b'\x02' if (y % 2 == 0) else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')


def _rfc6979_nonce(msg_hash: bytes, privkey_bytes: bytes) -> int:
    """Generate deterministic nonce k per RFC 6979 for Secp256k1."""
    V = b'\x01' * 32
    K = b'\x00' * 32
    
    K = hmac.new(K, V + b'\x00' + privkey_bytes + msg_hash, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    K = hmac.new(K, V + b'\x01' + privkey_bytes + msg_hash, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    
    while True:
        V = hmac.new(K, V, hashlib.sha256).digest()
        k = int.from_bytes(V, 'big')
        if 1 <= k < _N:
            return k
        K = hmac.new(K, V + b'\x00', hashlib.sha256).digest()
        V = hmac.new(K, V, hashlib.sha256).digest()


def ecdsa_sign(msg_hash: bytes, privkey_bytes: bytes) -> Tuple[int, int]:
    """
    Sign a 32-byte hash using Secp256k1 ECDSA with deterministic RFC 6979 nonce.
    Returns (r, s) tuple with canonical low-s (BIP 62).
    """
    if len(msg_hash) != 32 or len(privkey_bytes) != 32:
        raise ValueError("Message hash and private key must be exactly 32 bytes")
        
    z = int.from_bytes(msg_hash, 'big')
    d = int.from_bytes(privkey_bytes, 'big')
    if d <= 0 or d >= _N:
        raise ValueError("Invalid private key scalar")
        
    k = _rfc6979_nonce(msg_hash, privkey_bytes)
    pt = _point_mul(k, _G)
    assert pt is not None
    r = pt[0] % _N
    if r == 0:
        return ecdsa_sign(hashlib.sha256(msg_hash + b'1').digest(), privkey_bytes)
        
    k_inv = _mod_inverse(k, _N)
    s = (k_inv * (z + r * d)) % _N
    if s == 0:
        return ecdsa_sign(hashlib.sha256(msg_hash + b'2').digest(), privkey_bytes)
        
    # BIP 62 Low-S enforcement
    if s > (_N // 2):
        s = _N - s
        
    return (r, s)


def encode_der_signature(r: int, s: int) -> bytes:
    """Encode (r, s) integers into standard ASN.1 DER signature format."""
    def _encode_int(val: int) -> bytes:
        raw = val.to_bytes((val.bit_length() + 7) // 8 or 1, 'big')
        if raw[0] >= 0x80:
            raw = b'\x00' + raw
        return b'\x02' + bytes([len(raw)]) + raw
        
    r_enc = _encode_int(r)
    s_enc = _encode_int(s)
    body = r_enc + s_enc
    return b'\x30' + bytes([len(body)]) + body


def decode_der_signature(der: bytes) -> Tuple[int, int]:
    """Decode ASN.1 DER signature format into (r, s) integers."""
    if len(der) < 8 or der[0] != 0x30:
        raise ValueError("Invalid DER signature format")
        
    tot_len = der[1]
    if len(der) != tot_len + 2:
        raise ValueError("DER signature length mismatch")
        
    pos = 2
    if der[pos] != 0x02:
        raise ValueError("Expected integer marker for r")
    r_len = der[pos+1]
    r_bytes = der[pos+2:pos+2+r_len]
    r = int.from_bytes(r_bytes, 'big')
    
    pos = pos + 2 + r_len
    if der[pos] != 0x02:
        raise ValueError("Expected integer marker for s")
    s_len = der[pos+1]
    s_bytes = der[pos+2:pos+2+s_len]
    s = int.from_bytes(s_bytes, 'big')
    
    return (r, s)


def ecdsa_verify(msg_hash: bytes, pubkey_bytes: bytes, r: int, s: int) -> bool:
    """Verify Secp256k1 ECDSA signature."""
    if len(msg_hash) != 32:
        return False
    if not (1 <= r < _N and 1 <= s < _N):
        return False
        
    # Parse public key
    try:
        if len(pubkey_bytes) == 33 and pubkey_bytes[0] in (0x02, 0x03):
            px = int.from_bytes(pubkey_bytes[1:], 'big')
            # y^2 = x^3 + 7 (mod P)
            y_sq = (pow(px, 3, _P) + 7) % _P
            py = pow(y_sq, (_P + 1) // 4, _P)
            if pow(py, 2, _P) != y_sq:
                return False
            if (py % 2 == 0 and pubkey_bytes[0] != 0x02) or (py % 2 != 0 and pubkey_bytes[0] != 0x03):
                py = _P - py
            pub_pt = (px, py)
        elif len(pubkey_bytes) == 65 and pubkey_bytes[0] == 0x04:
            px = int.from_bytes(pubkey_bytes[1:33], 'big')
            py = int.from_bytes(pubkey_bytes[33:], 'big')
            if (pow(py, 2, _P) - (pow(px, 3, _P) + 7)) % _P != 0:
                return False
            pub_pt = (px, py)
        else:
            return False
    except Exception:
        return False
        
    z = int.from_bytes(msg_hash, 'big')
    w = _mod_inverse(s, _N)
    u1 = (z * w) % _N
    u2 = (r * w) % _N
    
    p1 = _point_mul(u1, _G)
    p2 = _point_mul(u2, pub_pt)
    res = _point_add(p1, p2)
    
    if res is None:
        return False
    return (res[0] % _N) == r
