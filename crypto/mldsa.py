"""
QuantyCoin Post-Quantum Cryptography - NIST FIPS 204 ML-DSA (CRYSTALS-Dilithium)
Standardized lattice-based digital signatures for quantum-resistant transaction authorization.
Zero-Mock Implementation with Native Acceleration & Strict Fail-Closed Verification (Zero Pseudo-Crypto Fallbacks).
"""

import os
import sys
import ctypes
import hashlib
from typing import Tuple, Optional


PUBLIC_KEY_BYTES = 1312
SECRET_KEY_BYTES = 2560
SIGNATURE_BYTES = 2420
SEED_BYTES = 32

_native_lib = None
_lib_loaded = False


def _find_or_build_native_lib():
    global _native_lib, _lib_loaded
    if _lib_loaded:
        return _native_lib

    # 1. Search existing compiled locations
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "src", "crypto", "libqtydilithium.dll"),
        os.path.join(base_dir, "src", "crypto", "libqtydilithium.so"),
        os.path.join(base_dir, "src", "crypto", "libqtydilithium.dylib"),
    ]

    for c in candidates:
        if os.path.exists(c):
            try:
                lib = ctypes.CDLL(c)
                _setup_lib_signatures(lib)
                _native_lib = lib
                _lib_loaded = True
                return _native_lib
            except Exception:
                continue

    # 2. If native shared library is missing on Linux/Unix, attempt self-healing compilation if sources & C compiler exist
    ref_dir = os.path.join(base_dir, "src", "crypto", "dilithium", "ref")
    wrapper_src = os.path.join(base_dir, "src", "crypto", "dilithium_wrapper.c")
    c_sources = [
        wrapper_src,
        os.path.join(ref_dir, "fips202.c"),
        os.path.join(ref_dir, "ntt.c"),
        os.path.join(ref_dir, "packing.c"),
        os.path.join(ref_dir, "poly.c"),
        os.path.join(ref_dir, "polyvec.c"),
        os.path.join(ref_dir, "randombytes.c"),
        os.path.join(ref_dir, "reduce.c"),
        os.path.join(ref_dir, "rounding.c"),
        os.path.join(ref_dir, "sign.c"),
        os.path.join(ref_dir, "symmetric-shake.c"),
    ]
    if all(os.path.exists(s) for s in c_sources):
        import shutil
        import subprocess
        cc = os.environ.get("CC") or shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
        if cc:
            target_so = os.path.join(base_dir, "src", "crypto", "libqtydilithium.so")
            try:
                cmd = [
                    cc, "-O3", "-shared", "-fPIC", "-DDILITHIUM_MODE=2",
                    f"-I{os.path.join(base_dir, 'src', 'crypto')}",
                    f"-I{ref_dir}",
                    *c_sources,
                    "-o", target_so
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if res.returncode == 0 and os.path.exists(target_so):
                    lib = ctypes.CDLL(target_so)
                    _setup_lib_signatures(lib)
                    _native_lib = lib
                    _lib_loaded = True
                    return _native_lib
            except Exception:
                pass

    _lib_loaded = True
    return None


def _setup_lib_signatures(lib):
    lib.qty_dilithium_keypair_from_seed.restype = ctypes.c_int
    lib.qty_dilithium_keypair_from_seed.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p
    ]
    lib.qty_dilithium_sign.restype = ctypes.c_int
    lib.qty_dilithium_sign.argtypes = [
        ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_char_p
    ]
    lib.qty_dilithium_verify.restype = ctypes.c_int
    lib.qty_dilithium_verify.argtypes = [
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_char_p
    ]


class CryptographicBackendUnavailableError(RuntimeError):
    """Raised when native post-quantum cryptographic library (FIPS 204) is unavailable."""
    pass


def get_native_lib():
    """Retrieve verified native FIPS 204 library or raise CryptographicBackendUnavailableError."""
    lib = _find_or_build_native_lib()
    if lib is None:
        raise CryptographicBackendUnavailableError(
            "Genuine NIST FIPS 204 ML-DSA backend (libqtydilithium) is unavailable. "
            "In accordance with R004/R008 security rules, insecure pseudo-cryptographic fallbacks are forbidden."
        )
    return lib


class MLDSAKey:
    """NIST FIPS 204 ML-DSA-44 / Dilithium2 Key Pair."""
    def __init__(self, public_key: bytes, secret_key: bytes):
        if len(public_key) != PUBLIC_KEY_BYTES:
            raise ValueError(f"Invalid ML-DSA public key length: {len(public_key)} != {PUBLIC_KEY_BYTES}")
        if len(secret_key) != SECRET_KEY_BYTES:
            raise ValueError(f"Invalid ML-DSA secret key length: {len(secret_key)} != {SECRET_KEY_BYTES}")
        self.public_key = public_key
        self.secret_key = secret_key

    @classmethod
    def from_seed(cls, seed: bytes) -> 'MLDSAKey':
        """Deterministically derive keypair from 32-byte seed using native FIPS 204 engine."""
        if len(seed) != SEED_BYTES:
            raise ValueError(f"Seed must be {SEED_BYTES} bytes, got {len(seed)}")
        
        lib = get_native_lib()
        pk = ctypes.create_string_buffer(PUBLIC_KEY_BYTES)
        sk = ctypes.create_string_buffer(SECRET_KEY_BYTES)
        ret = lib.qty_dilithium_keypair_from_seed(pk, sk, seed)
        if ret != 0:
            raise RuntimeError("Native ML-DSA key generation failed")
        return cls(pk.raw, sk.raw)

    @classmethod
    def generate(cls) -> 'MLDSAKey':
        """Generate random secure ML-DSA keypair using native FIPS 204 engine."""
        return cls.from_seed(os.urandom(SEED_BYTES))

    def sign(self, message: bytes, ctx: bytes = b"") -> bytes:
        """Sign message and return detached signature."""
        return mldsa_sign(message, self.secret_key, ctx)

    def verify(self, message: bytes, signature: bytes, ctx: bytes = b"") -> bool:
        """Verify detached signature against public key."""
        return mldsa_verify(message, signature, self.public_key, ctx)


def mldsa_keypair(seed: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Generate (public_key, secret_key) bytes using native FIPS 204 engine."""
    if seed is None:
        seed = os.urandom(SEED_BYTES)
    k = MLDSAKey.from_seed(seed)
    return k.public_key, k.secret_key


def mldsa_sign(message: bytes, secret_key: bytes, ctx: bytes = b"") -> bytes:
    """Create ML-DSA signature for message using native FIPS 204 engine."""
    if len(secret_key) != SECRET_KEY_BYTES:
        raise ValueError(f"Secret key must be {SECRET_KEY_BYTES} bytes")
    
    lib = get_native_lib()
    sig = ctypes.create_string_buffer(SIGNATURE_BYTES)
    siglen = ctypes.c_size_t(SIGNATURE_BYTES)
    ctx_ptr = ctx if ctx else None
    ret = lib.qty_dilithium_sign(
        sig, ctypes.byref(siglen),
        message, len(message),
        ctx_ptr, len(ctx),
        secret_key
    )
    if ret != 0:
        raise RuntimeError("Native ML-DSA signing failed")
    return sig.raw[:siglen.value]


def mldsa_verify(message: bytes, signature: bytes, public_key: bytes, ctx: bytes = b"") -> bool:
    """Verify ML-DSA signature against public key using native FIPS 204 engine."""
    if len(public_key) != PUBLIC_KEY_BYTES:
        return False
    if len(signature) != SIGNATURE_BYTES:
        return False

    lib = get_native_lib()
    ctx_ptr = ctx if ctx else None
    ret = lib.qty_dilithium_verify(
        signature, len(signature),
        message, len(message),
        ctx_ptr, len(ctx),
        public_key
    )
    return ret == 0

