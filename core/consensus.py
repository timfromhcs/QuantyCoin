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


def get_block_subsidy(height: int) -> int:
    """Calculate base block reward in Satoshis for a given height."""
    halvings = height // SUBSIDY_HALVING_INTERVAL
    if halvings >= 64:
        return 0
    subsidy_qty = GENESIS_BLOCK_REWARD / (2 ** halvings)
    return int(subsidy_qty * 100_000_000)


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
