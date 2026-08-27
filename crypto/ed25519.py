"""
QuantyCoin Core Cryptography - Ed25519 Digital Signature Engine
RFC 8032 Compliant High-Performance Pure Python Implementation
"""

import hashlib
from typing import Tuple

_b = 256
_q = 2**255 - 19
_l = 2**252 + 27742317777372353535851937790883648493
_d = -121665 * pow(121666, _q - 2, _q) % _q
_I = pow(2, (_q - 1) // 4, _q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_d * y * y + 1, _q - 2, _q)
    x = pow(xx, (_q + 3) // 8, _q)
    if (x * x - xx) % _q != 0:
        x = (x * _I) % _q
    if x % 2 != 0:
        x = _q - x
    return x


_By = 4 * pow(5, _q - 2, _q) % _q
_Bx = _xrecover(_By)
_B = (_Bx, _By)


def _ed_add(P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * pow(1 + _d * x1 * x2 * y1 * y2, _q - 2, _q) % _q
    y3 = (y1 * y2 + x1 * x2) * pow(1 - _d * x1 * x2 * y1 * y2, _q - 2, _q) % _q
    return (x3, y3)


def _ed_scalarmult(P: Tuple[int, int], e: int) -> Tuple[int, int]:
    if e == 0:
        return (0, 1)
    Q = _ed_scalarmult(P, e // 2)
    Q = _ed_add(Q, Q)
    if e & 1:
        Q = _ed_add(Q, P)
    return Q


def _encodeint(y: int) -> bytes:
    return y.to_bytes(32, 'little')


def _decodeint(b: bytes) -> int:
    return int.from_bytes(b, 'little')


def _encodepoint(P: Tuple[int, int]) -> bytes:
    x, y = P
    bits = [(y >> i) & 1 for i in range(_b - 1)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(_b // 8))


def _decodepoint(s: bytes) -> Tuple[int, int]:
    if len(s) != 32:
        raise ValueError("Encoded point must be 32 bytes")
    y = int.from_bytes(s, 'little') & ((1 << 255) - 1)
    x_sign = (s[31] >> 7) & 1
    x = _xrecover(y)
    if (x & 1) != x_sign:
        x = _q - x
    P = (x, y)
    if not _isoncurve(P):
        raise ValueError("Decoded point not on curve")
    return P


def _isoncurve(P: Tuple[int, int]) -> bool:
    x, y = P
    return (-x * x + y * y - 1 - _d * x * x * y * y) % _q == 0


def _secret_expand(sk: bytes) -> Tuple[int, bytes]:
    h = hashlib.sha512(sk).digest()
    a_bytes = bytearray(h[:32])
    a_bytes[0] &= 248
    a_bytes[31] &= 127
    a_bytes[31] |= 64
    a = int.from_bytes(a_bytes, 'little')
    prefix = h[32:]
    return a, prefix


def ed25519_public_key(sk: bytes) -> bytes:
    """Derive 32-byte Ed25519 public key from 32-byte secret key."""
    a, _ = _secret_expand(sk)
    A = _ed_scalarmult(_B, a)
    return _encodepoint(A)


def ed25519_sign(msg: bytes, sk: bytes, pk: bytes) -> bytes:
    """Sign message with Ed25519 (returns 64-byte signature)."""
    a, prefix = _secret_expand(sk)
    r = _decodeint(hashlib.sha512(prefix + msg).digest()) % _l
    R = _ed_scalarmult(_B, r)
    R_bytes = _encodepoint(R)
    k = _decodeint(hashlib.sha512(R_bytes + pk + msg).digest()) % _l
    S = (r + k * a) % _l
    return R_bytes + _encodeint(S)


def ed25519_verify(sig: bytes, msg: bytes, pk: bytes) -> bool:
    """Verify 64-byte Ed25519 signature."""
    if len(sig) != 64 or len(pk) != 32:
        return False
    try:
        R_bytes = sig[:32]
        S_bytes = sig[32:]
        R = _decodepoint(R_bytes)
        A = _decodepoint(pk)
        S = _decodeint(S_bytes)
        if S >= _l:
            return False
        k = _decodeint(hashlib.sha512(R_bytes + pk + msg).digest()) % _l
        SB = _ed_scalarmult(_B, S)
        RkA = _ed_add(R, _ed_scalarmult(A, k))
        return SB == RkA
    except Exception:
        return False
