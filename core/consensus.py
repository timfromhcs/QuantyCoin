"""
QuantyCoin Core - Consensus Rules, Difficulty Retargeting & Halving Schedule
Zero-Mock Implementation (LWMA, Halving Matrix, Fee Distribution Rules)
"""

from typing import List, Tuple
from .genesis_constants import (
    TARGET_BLOCK_TIME, SUBSIDY_HALVING_INTERVAL,
    GENESIS_BLOCK_REWARD, GENESIS_BITS
)


# PoW Limit Target (highest allowable target / lowest difficulty)
POW_LIMIT_BITS = 0x1e0fffff
POW_LIMIT_TARGET = 0x00000fffff000000000000000000000000000000000000000000000000000000

# Dual Proof-of-Work Mining Lanes
POW_TYPE_SHA256D = 0
POW_TYPE_GENERAL_PURPOSE = 1

LANE_WEIGHT_SHA256D = 1
LANE_WEIGHT_GENERAL_PURPOSE = 2048
LANE_TARGET_SPACING = 120  # 120 seconds per lane for 60s combined network interval


def get_block_subsidy(height: int, pow_type: int = POW_TYPE_SHA256D) -> int:
    """Calculate block reward in Satoshis for a given height and PoW lane."""
    halvings = height // SUBSIDY_HALVING_INTERVAL
    if halvings >= 64:
        return 0
    subsidy_qty = GENESIS_BLOCK_REWARD / (2 ** halvings)
    if pow_type == POW_TYPE_GENERAL_PURPOSE:
        # Lane B receives 50% of base subsidy
        subsidy_qty *= 0.5
    return int(subsidy_qty * 100_000_000)


def calculate_next_work_required_dual(headers: List['BlockHeader'], pow_type: int = POW_TYPE_SHA256D, target_spacing: int = LANE_TARGET_SPACING, n: int = 45) -> int:
    """
    Independent LWMA-1 difficulty adjustment for a specific PoW mining lane.
    Filters headers by pow_type to maintain isolated difficulty histories.
    """
    lane_headers = [h for h in headers if h.pow_type == pow_type]
    if len(lane_headers) < n + 1:
        return POW_LIMIT_BITS
    return calculate_next_work_required_lwma(lane_headers, target_spacing=target_spacing, n=n)


def calculate_next_work_required_lwma(headers: List['BlockHeader'], target_spacing: int = TARGET_BLOCK_TIME, n: int = 45) -> int:
    """
    Linear-Weighted Moving Average (LWMA-1) Difficulty Adjustment Algorithm.
    Provides responsive, oscillation-free retargeting every single block.
    n: Window size (e.g. 45 blocks).
    """
    from .block import BlockHeader
    
    if len(headers) < n + 1:
        return POW_LIMIT_BITS
        
    recent = headers[-(n+1):]
    
    sum_targets = 0
    t = 0
    weight = 0
    
    # Calculate weighted target sum and weighted solve times
    for i in range(1, n + 1):
        solve_time = recent[i].timestamp - recent[i-1].timestamp
        # Clamp individual solve time to prevent timestamp manipulation attacks
        solve_time = max(-6 * target_spacing, min(solve_time, 6 * target_spacing))
        
        target = recent[i].get_target()
        sum_targets += target
        t += solve_time * i
        weight += i
        
    avg_target = sum_targets // n
    # Expected weighted time: target_spacing * weight
    expected_t = target_spacing * weight
    
    if t <= 0:
        t = 1
        
    # next_target = avg_target * (t / expected_t)
    next_target = (avg_target * t) // expected_t
    
    # Clamp to POW_LIMIT
    if next_target > POW_LIMIT_TARGET or next_target <= 0:
        next_target = POW_LIMIT_TARGET
        
    return target_to_bits(next_target)


def target_to_bits(target: int) -> int:
    """Convert integer target to compact uint32 bits."""
    nbytes = (target.bit_length() + 7) // 8
    if nbytes <= 3:
        compact = (target << (8 * (3 - nbytes))) & 0x00FFFFFF
    else:
        compact = (target >> (8 * (nbytes - 3))) & 0x00FFFFFF
        
    if compact & 0x00800000:
        compact >>= 8
        nbytes += 1
    return (nbytes << 24) | compact


def bits_to_target(bits: int) -> int:
    """Convert compact uint32 bits to integer target."""
    exponent = bits >> 24
    coefficient = bits & 0x00FFFFFF
    if exponent <= 3:
        target = coefficient >> (8 * (3 - exponent))
    else:
        target = coefficient << (8 * (exponent - 3))
    return target
