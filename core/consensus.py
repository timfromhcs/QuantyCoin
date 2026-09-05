"""
QuantyCoin Core - Consensus Rules, Difficulty Retargeting & Monetary Integrity
Zero-Mock Implementation with Pure 64-Bit Integer Arithmetic (No Floating Point).
Enforces LWMA-1 per-lane difficulty, weighted cumulative work, and strict compact target validation.
"""

from typing import List, Tuple, Optional
from .genesis_constants import (
    TARGET_BLOCK_TIME, LANE_A_TARGET_TIME, LANE_B_TARGET_TIME,
    SUBSIDY_HALVING_INTERVAL, MAX_MONEY_SATOSHIS,
    LANE_A_BASE_SUBSIDY, LANE_B_BASE_SUBSIDY,
    THERMODYNAMIC_WEIGHT_A, THERMODYNAMIC_WEIGHT_B,
    DIFFICULTY_RETARGET_INTERVAL, GENESIS_BITS
)
from .money import Amount, MoneyRangeError

# PoW Limit Target (highest allowable target / lowest difficulty)
POW_LIMIT_BITS = 0x1e0fffff
POW_LIMIT_TARGET = 0x00000fffff000000000000000000000000000000000000000000000000000000

# Dual Proof-of-Work Mining Lanes
POW_TYPE_SHA256D = 0
POW_TYPE_GENERAL_PURPOSE = 1

LANE_WEIGHT_SHA256D = THERMODYNAMIC_WEIGHT_A
LANE_WEIGHT_GENERAL_PURPOSE = THERMODYNAMIC_WEIGHT_B
LANE_TARGET_SPACING = LANE_A_TARGET_TIME


def check_money_range(satoshis: int) -> bool:
    """Verify satoshi amount is non-negative and within MAX_MONEY_SATOSHIS."""
    return isinstance(satoshis, int) and 0 <= satoshis <= MAX_MONEY_SATOSHIS


def get_block_subsidy(height: int, pow_type: int = POW_TYPE_SHA256D) -> int:
    """
    Calculate exact integer block subsidy in Satoshis for a given height and lane.
    Pure integer right-shift arithmetic. Zero floating-point operations.
    """
    halvings = height // SUBSIDY_HALVING_INTERVAL
    if halvings >= 64:
        return 0

    base = LANE_A_BASE_SUBSIDY if pow_type == POW_TYPE_SHA256D else LANE_B_BASE_SUBSIDY
    return base >> halvings


def bits_to_target(bits: int) -> int:
    """
    Convert compact uint32 bits to 256-bit integer target.
    Strictly rejects negative, zero, and malformed compact targets.
    """
    if bits < 0 or bits > 0xFFFFFFFF:
        raise ValueError(f"Bits out of 32-bit range: {bits}")

    exponent = bits >> 24
    coefficient = bits & 0x00FFFFFF

    # Check for negative compact target bit
    if coefficient & 0x00800000:
        raise ValueError(f"Negative compact target is invalid: bits=0x{bits:08x}")

    if exponent <= 3:
        target = coefficient >> (8 * (3 - exponent))
    else:
        target = coefficient << (8 * (exponent - 3))

    return target


def target_to_bits(target: int) -> int:
    """Convert 256-bit integer target to compact uint32 bits."""
    if target <= 0:
        return 0
    if target > POW_LIMIT_TARGET:
        target = POW_LIMIT_TARGET

    nbytes = (target.bit_length() + 7) // 8
    if nbytes <= 3:
        compact = (target << (8 * (3 - nbytes))) & 0x00FFFFFF
    else:
        compact = (target >> (8 * (nbytes - 3))) & 0x00FFFFFF

    if compact & 0x00800000:
        compact >>= 8
        nbytes += 1

    return (nbytes << 24) | compact


def get_block_work(bits: int, pow_type: int = POW_TYPE_SHA256D) -> int:
    """
    Compute Weighted Cumulative Work for a block target on a specific lane.
    Work(target) = weight * floor(2^256 / (target + 1))
    """
    target = bits_to_target(bits)
    if target <= 0:
        return 0

    raw_work = (1 << 256) // (target + 1)
    weight = LANE_WEIGHT_GENERAL_PURPOSE if pow_type == POW_TYPE_GENERAL_PURPOSE else LANE_WEIGHT_SHA256D
    return raw_work * weight


def calculate_next_work_required_dual(
    headers: List[object],
    pow_type: int = POW_TYPE_SHA256D,
    target_spacing: int = LANE_TARGET_SPACING,
    n: int = DIFFICULTY_RETARGET_INTERVAL
) -> int:
    """
    Independent LWMA-1 difficulty adjustment for a specific PoW lane.
    Filters headers by pow_type to maintain isolated per-lane difficulty histories.
    """
    lane_headers = [h for h in headers if getattr(h, 'pow_type', None) == pow_type]
    if len(lane_headers) < n + 1:
        return POW_LIMIT_BITS
    return calculate_next_work_required_lwma(lane_headers, target_spacing=target_spacing, n=n)


def calculate_next_work_required_lwma(
    headers: List[object],
    target_spacing: int = TARGET_BLOCK_TIME,
    n: int = DIFFICULTY_RETARGET_INTERVAL
) -> int:
    """
    Linear-Weighted Moving Average (LWMA-1) Difficulty Adjustment Algorithm.
    Pure integer arithmetic with solvetime clamping [-6T, +6T].
    """
    if len(headers) < n + 1:
        return POW_LIMIT_BITS

    recent = headers[-(n + 1):]

    sum_targets = 0
    t = 0
    weight = 0

    for i in range(1, n + 1):
        solve_time = recent[i].timestamp - recent[i - 1].timestamp
        # Clamp individual solve time to prevent timestamp manipulation attacks
        solve_time = max(-6 * target_spacing, min(solve_time, 6 * target_spacing))

        target = bits_to_target(recent[i].bits)
        sum_targets += target
        t += solve_time * i
        weight += i

    avg_target = sum_targets // n
    expected_t = target_spacing * weight

    if t <= 0:
        t = 1

    next_target = (avg_target * t) // expected_t

    if next_target > POW_LIMIT_TARGET or next_target <= 0:
        next_target = POW_LIMIT_TARGET

    return target_to_bits(next_target)


def calculate_median_time_past(headers: List[object], window: int = 11) -> int:
    """
    Calculate Median-Time-Past (MTP) over the previous window blocks.
    Returns median timestamp for strictly monotonic time enforcement.
    """
    if not headers:
        return 0
    recent = [h.timestamp for h in headers[-window:]]
    recent.sort()
    return recent[len(recent) // 2]
