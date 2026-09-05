"""
QuantyCoin QTY4 Independent Reference Implementation.

READABILITY-FIRST, STDIB-ONLY, DELIBERATELY STRUCTURALLY INDEPENDENT from
``core/`` production code. Used exclusively for differential verification:
production vs reference must agree on deterministic vectors.

Covers: compact target conversion, PoW target validation, work,
difficulty (LWMA-1), MTP, subsidy, money-range, varint, txid/wtxid,
merkle root, block/header serialization, bech32/bech32m segwit addresses,
fork-choice comparison.

No imports from core/, crypto/, network/, miner/, node/, wallet/.
Only Python standard library.
"""

import hashlib
import struct

# ---- Canonical QTY4 constants (mirrors spec/qty4/*.json) ----
PROTOCOL_VERSION = 70040
CHAIN_ID = "quantycoin-4.0"
GENESIS_HASH = "000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3"
GENESIS_MERKLE_ROOT = "3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea"
GENESIS_TIMESTAMP = 1788614400
GENESIS_BITS = 0x1E0FFFFF
GENESIS_NONCE = 2951011
POW_LIMIT_BITS = 0x1E0FFFFF
POW_LIMIT_TARGET = 0x00000FFFFF000000000000000000000000000000000000000000000000000000
MAX_MONEY_SATOSHIS = 21000000 * 100_000_000
MAX_BLOCK_SIZE = 32 * 1024 * 1024
COINBASE_MATURITY = 100
MTP_WINDOW = 11
FUTURE_TIME_LIMIT = 7200
SUBSIDY_HALVING_INTERVAL = 2100000
LANE_A_BASE_SUBSIDY = 50 * 100_000_000
LANE_B_BASE_SUBSIDY = 25 * 100_000_000
WEIGHT_A = 1
WEIGHT_B = 2048
LANE_A = 0
LANE_B = 1
LWMA_WINDOW = 45
LANE_TARGET_SPACING = 120
MAGIC_MAINNET = bytes([0x51, 0x54, 0x59, 0x34])


def check_money_range(value) -> bool:
    return isinstance(value, int) and 0 <= value <= MAX_MONEY_SATOSHIS


def block_subsidy(height: int, lane: int = LANE_A) -> int:
    if not isinstance(height, int) or height < 0:
        raise ValueError("height must be non-negative int")
    halvings = height // SUBSIDY_HALVING_INTERVAL
    if halvings >= 64:
        return 0
    base = LANE_A_BASE_SUBSIDY if lane == LANE_A else LANE_B_BASE_SUBSIDY
    return base >> halvings


def compact_to_target(bits: int) -> int:
    """Independent compact->target conversion. Strict: rejects sign bit."""
    if not isinstance(bits, int):
        raise TypeError("bits must be int")
    if bits < 0 or bits > 0xFFFFFFFF:
        raise ValueError("bits out of uint32 range")
    exp = (bits >> 24) & 0xFF
    coef = bits & 0x00FFFFFF
    if coef & 0x00800000:
        raise ValueError("negative compact target")
    if exp <= 3:
        return coef >> (8 * (3 - exp))
    return coef << (8 * (exp - 3))


def target_to_compact(target: int) -> int:
    if not isinstance(target, int):
        raise TypeError("target must be int")
    if target <= 0:
        return 0
    if target > POW_LIMIT_TARGET:
        target = POW_LIMIT_TARGET
    size = (target.bit_length() + 7) // 8
    if size <= 3:
        word = (target << (8 * (3 - size))) & 0x00FFFFFF
    else:
        word = (target >> (8 * (size - 3))) & 0x00FFFFFF
    if word & 0x00800000:
        word >>= 8
        size += 1
    return ((size << 24) | word) & 0xFFFFFFFF


def block_work(bits: int, lane: int = LANE_A) -> int:
    target = compact_to_target(bits)
    if target <= 0:
        return 0
    raw = (1 << 256) // (target + 1)
    weight = WEIGHT_B if lane == LANE_B else WEIGHT_A
    return raw * weight


def passes_pow(pow_hash_le: bytes, bits: int) -> bool:
    """pow_hash_le: 32-byte little-endian hash. Returns True iff hash <= target."""
    if len(pow_hash_le) != 32:
        raise ValueError("pow hash must be 32 bytes")
    target = compact_to_target(bits)
    if target <= 0:
        return False
    value = int.from_bytes(pow_hash_le[::-1], "big")
    return value <= target


def median_time_past(timestamps, window: int = MTP_WINDOW) -> int:
    if not timestamps:
        return 0
    recent = sorted(timestamps[-window:])
    return recent[len(recent) // 2]


def lwma_next_bits(entries, target_spacing: int = LANE_TARGET_SPACING,
                   window: int = LWMA_WINDOW):
    """entries: list of (timestamp:int, bits:int) oldest->newest for ONE lane."""
    if len(entries) < window + 1:
        return POW_LIMIT_BITS
    recent = entries[-(window + 1):]
    acc_targets = 0
    acc_t = 0
    acc_w = 0
    for i in range(1, window + 1):
        dt = recent[i][0] - recent[i - 1][0]
        lo = -6 * target_spacing
        hi = 6 * target_spacing
        if dt < lo:
            dt = lo
        elif dt > hi:
            dt = hi
        acc_targets += compact_to_target(recent[i][1])
        acc_t += dt * i
        acc_w += i
    avg = acc_targets // window
    expect = target_spacing * acc_w
    t = acc_t if acc_t > 0 else 1
    nxt = (avg * t) // expect
    if nxt <= 0 or nxt > POW_LIMIT_TARGET:
        nxt = POW_LIMIT_TARGET
    return target_to_compact(nxt)


# ---- Serialization helpers (independent varint/codec) ----

def encode_varint(n: int) -> bytes:
    if n < 0:
        raise ValueError("varint must be non-negative")
    if n < 0xFD:
        return struct.pack("<B", n)
    if n <= 0xFFFF:
        return b"\xfd" + struct.pack("<H", n)
    if n <= 0xFFFFFFFF:
        return b"\xfe" + struct.pack("<I", n)
    if n <= 0xFFFFFFFFFFFFFFFF:
        return b"\xff" + struct.pack("<Q", n)
    raise ValueError("varint overflow")


def decode_varint(buf: bytes, offset: int = 0):
    if offset >= len(buf):
        raise ValueError("truncated varint")
    first = buf[offset]
    if first < 0xFD:
        return first, offset + 1
    if first == 0xFD:
        if offset + 3 > len(buf):
            raise ValueError("truncated varint16")
        return struct.unpack_from("<H", buf, offset + 1)[0], offset + 3
    if first == 0xFE:
        if offset + 5 > len(buf):
            raise ValueError("truncated varint32")
        return struct.unpack_from("<I", buf, offset + 1)[0], offset + 5
    if offset + 9 > len(buf):
        raise ValueError("truncated varint64")
    return struct.unpack_from("<Q", buf, offset + 1)[0], offset + 9


def hash256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def merkle_root(txids_le: list) -> bytes:
    """txids_le: list of 32-byte little-endian txids. Returns LE root."""
    if not txids_le:
        return b"\x00" * 32
    level = list(txids_le)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(hash256(level[i] + level[i + 1]))
        level = nxt
    return level[0]


def serialize_header(version: int, prev_le: bytes, root_le: bytes,
                     timestamp: int, bits: int, nonce: int) -> bytes:
    if len(prev_le) != 32 or len(root_le) != 32:
        raise ValueError("prev/root must be 32 bytes")
    return (struct.pack("<i", version) + prev_le + root_le
            + struct.pack("<I", timestamp) + struct.pack("<I", bits)
            + struct.pack("<I", nonce))


def deserialize_header(buf: bytes):
    if len(buf) < 80:
        raise ValueError("header too short")
    version = struct.unpack_from("<i", buf, 0)[0]
    prev_le = bytes(buf[4:36])
    root_le = bytes(buf[36:68])
    timestamp = struct.unpack_from("<I", buf, 68)[0]
    bits = struct.unpack_from("<I", buf, 72)[0]
    nonce = struct.unpack_from("<I", buf, 76)[0]
    return {
        "version": version,
        "pow_type": (version >> 16) & 0xFFFF,
        "prev": prev_le,
        "root": root_le,
        "timestamp": timestamp,
        "bits": bits,
        "nonce": nonce,
    }, 80


def header_hash(header_bytes_80: bytes) -> bytes:
    if len(header_bytes_80) != 80:
        raise ValueError("header must be 80 bytes")
    return hash256(header_bytes_80)


# ---- Bech32/Bech32m (independent transcription for differential testing) ----

_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_CHARSET_MAP = {c: i for i, c in enumerate(_CHARSET)}
_BECH32 = 1
_BECH32M = 0x2BC830A3
_GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]


def _polymod(values) -> int:
    chk = 1
    for v in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i in range(5):
            if (top >> i) & 1:
                chk ^= _GEN[i]
    return chk


def _hrp_expand(hrp: str):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _verify(hrp: str, data):
    c = _polymod(_hrp_expand(hrp) + list(data))
    if c == _BECH32:
        return _BECH32
    if c == _BECH32M:
        return _BECH32M
    return None


def segwit_decode(hrp: str, addr: str):
    if any(ord(c) < 33 or ord(c) > 126 for c in addr):
        return None, None
    if addr.lower() != addr and addr.upper() != addr:
        return None, None
    low = addr.lower()
    pos = low.rfind("1")
    if pos < 1 or pos + 7 > len(low) or len(low) > 90:
        return None, None
    tail = low[pos + 1:]
    if any(c not in _CHARSET_MAP for c in tail):
        return None, None
    if low[:pos] != hrp:
        return None, None
    nums = [_CHARSET_MAP[c] for c in tail]
    spec = _verify(hrp, nums)
    if spec is None:
        return None, None
    payload = nums[:-6]
    if not payload:
        return None, None
    version = payload[0]
    if version == 0 and spec != _BECH32:
        return None, None
    if version > 0 and spec != _BECH32M:
        return None, None
    prog = _convert(payload[1:], 5, 8, False)
    if prog is None or len(prog) < 2 or len(prog) > 40:
        return None, None
    return version, bytes(prog)


def _convert(data, frm: int, to: int, pad: bool):
    acc = 0
    bits = 0
    out = []
    top = (1 << to) - 1
    mask = (1 << (frm + to - 1)) - 1
    for v in data:
        if v < 0 or (v >> frm):
            return None
        acc = ((acc << frm) | v) & mask
        bits += frm
        while bits >= to:
            bits -= to
            out.append((acc >> bits) & top)
    if pad:
        if bits:
            out.append((acc << (to - bits)) & top)
    elif bits >= frm or ((acc << (to - bits)) & top):
        return None
    return out


def select_tip(a_height: int, a_work: int, b_height: int, b_work: int) -> str:
    """Fork choice: greatest cumulative work wins; tie -> greater height; else 'a'."""
    if b_work != a_work:
        return "b" if b_work > a_work else "a"
    if b_height != a_height:
        return "b" if b_height > a_height else "a"
    return "a"
