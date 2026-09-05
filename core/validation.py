"""
QuantyCoin Core - Authoritative Consensus Validation Pipeline
Implements the formal 12-stage consensus verification engine:
  1. CheckMoney
  2. CheckTransaction
  3. CheckPoW
  4. CheckCoinbase
  5. CheckBlock (Stateless structural syntax)
  6. CheckTimestamp (MTP & Future limits)
  7. CheckDifficulty (Per-lane LWMA-1 target matching)
  8. ContextualCheckBlock (Chain-dependent validation)
  9. CheckInputs (UTXO presence, double-spends, coinbase maturity)
  10. CheckScripts (Signatures: ECDSA, ML-DSA-44, Hybrid)
  11. ConnectBlock (Atomic state transition & undo generation)
  12. ActivateBestChain (Weighted cumulative work fork-choice)
"""

from typing import List, Tuple, Dict, Optional, Set
from .genesis_constants import (
    MAX_MONEY_SATOSHIS, MAX_BLOCK_SIZE, COINBASE_MATURITY,
    MTP_WINDOW, FUTURE_TIME_LIMIT,
    LANE_A_BASE_SUBSIDY, LANE_B_BASE_SUBSIDY
)
from .consensus import (
    get_block_subsidy, bits_to_target,
    calculate_next_work_required_dual,
    calculate_median_time_past,
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE,
    POW_LIMIT_BITS
)
from .money import Amount, MoneyRangeError
from .block import Block, BlockHeader
from .transaction import Transaction, TxIn, TxOut
from .utxo import UTXOSet


class ConsensusValidationError(ValueError):
    """Raised when consensus validation fails."""
    pass


def CheckMoney(amount: int) -> bool:
    """Stage 1: Verify monetary value is non-negative and <= MAX_MONEY_SATOSHIS."""
    return isinstance(amount, int) and 0 <= amount <= MAX_MONEY_SATOSHIS


def CheckTransaction(tx: Transaction) -> Tuple[bool, str]:
    """Stage 2: Stateless transaction structural validation."""
    return tx.validate_structure()


def CheckPoW(header: BlockHeader) -> Tuple[bool, str]:
    """Stage 3: Verify proof-of-work algorithm hash against target bits."""
    if header.pow_type not in (POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE):
        return False, f"Invalid PoW lane type: {header.pow_type}"

    try:
        target = bits_to_target(header.bits)
    except Exception as e:
        return False, f"Malformed compact target bits: {e}"

    if target <= 0:
        return False, "Target is non-positive"

    h_int = int.from_bytes(header.pow_hash[::-1], 'big')
    if h_int > target:
        return False, f"PoW hash {header.pow_hash_hex} exceeds target {target:064x}"

    return True, "Valid PoW"


def CheckCoinbase(tx: Transaction, height: int, pow_type: int, total_fees: int) -> Tuple[bool, str]:
    """Stage 4: Verify coinbase subsidy and fee collection bounds."""
    if not tx.is_coinbase():
        return False, "Transaction is not a coinbase"

    expected_subsidy = get_block_subsidy(height, pow_type)
    max_allowed = expected_subsidy + total_fees

    actual_reward = sum(out.value for out in tx.vout)
    if actual_reward > max_allowed:
        return False, f"Coinbase reward {actual_reward} exceeds allowed maximum {max_allowed} (subsidy {expected_subsidy} + fees {total_fees})"

    return True, "Valid Coinbase"


def CheckBlock(block: Block) -> Tuple[bool, str]:
    """Stage 5: Stateless block syntax, size, PoW, and Merkle tree validation."""
    # 1. PoW check
    pow_ok, pow_msg = CheckPoW(block.header)
    if not pow_ok:
        return False, pow_msg

    # 2. Block size check
    raw = block.serialize()
    if len(raw) > MAX_BLOCK_SIZE:
        return False, f"Block size {len(raw)} exceeds max limit {MAX_BLOCK_SIZE}"

    # 3. Transaction list check
    if not block.transactions:
        return False, "Block has no transactions"

    # 4. First tx must be coinbase
    if not block.transactions[0].is_coinbase():
        return False, "First transaction is not coinbase"

    # 5. Exactly 1 coinbase
    for i, tx in enumerate(block.transactions[1:], start=1):
        if tx.is_coinbase():
            return False, f"Transaction {i} is an illegal additional coinbase"

    # 6. Check individual transactions structurally
    for i, tx in enumerate(block.transactions):
        tx_ok, tx_msg = CheckTransaction(tx)
        if not tx_ok:
            return False, f"Transaction {i} failed CheckTransaction: {tx_msg}"

    # 7. Merkle root validation
    if not block.verify_merkle_root():
        return False, "Merkle root does not match computed root from transactions"

    return True, "Valid Block"


def CheckTimestamp(header: BlockHeader, prev_headers: List[BlockHeader], current_network_time: int) -> Tuple[bool, str]:
    """Stage 6: Enforce strictly monotonic MTP and future time bound."""
    mtp = calculate_median_time_past(prev_headers, window=MTP_WINDOW)
    if header.timestamp <= mtp:
        return False, f"Block timestamp {header.timestamp} <= Median-Time-Past {mtp}"

    if header.timestamp > current_network_time + FUTURE_TIME_LIMIT:
        return False, f"Block timestamp {header.timestamp} exceeds future limit {current_network_time + FUTURE_TIME_LIMIT}"

    return True, "Valid Timestamp"


def CheckDifficulty(header: BlockHeader, prev_headers: List[BlockHeader]) -> Tuple[bool, str]:
    """Stage 7: Enforce exact per-lane LWMA-1 difficulty target invariance."""
    expected_bits = calculate_next_work_required_dual(prev_headers, pow_type=header.pow_type)
    if header.bits != expected_bits:
        return False, f"Difficulty bits mismatch: block has 0x{header.bits:08x}, expected 0x{expected_bits:08x}"

    return True, "Valid Difficulty"


def ContextualCheckBlock(block: Block, prev_headers: List[BlockHeader], current_network_time: int) -> Tuple[bool, str]:
    """Stage 8: Contextual checks depending on parent chainstate."""
    # Check block version
    if (block.header.version & 0xFFFF) < 1:
        return False, f"Obsolete block version {block.header.version}"

    # Check timestamp
    ts_ok, ts_msg = CheckTimestamp(block.header, prev_headers, current_network_time)
    if not ts_ok:
        return False, ts_msg

    # Check difficulty
    diff_ok, diff_msg = CheckDifficulty(block.header, prev_headers)
    if not diff_ok:
        return False, diff_msg

    return True, "Valid Contextual Block"


def CheckInputs(tx: Transaction, utxo_set: UTXOSet, current_height: int) -> Tuple[bool, str, int]:
    """
    Stage 9: Verify UTXO availability, absence of double-spends, and coinbase maturity.
    Returns: (is_valid, message, total_fees)
    """
    if tx.is_coinbase():
        return True, "Coinbase has no parent inputs", 0

    total_in = 0
    for i, inp in enumerate(tx.vin):
        utxo = utxo_set.get_utxo(inp.prev_txid, inp.prev_vout)
        if utxo is None:
            return False, f"Input {i} references missing or already spent UTXO {inp.prev_txid[::-1].hex()}:{inp.prev_vout}", 0

        # Enforce coinbase maturity
        if utxo.is_coinbase:
            confirmations = current_height - utxo.block_height
            if confirmations < COINBASE_MATURITY:
                return False, f"Input {i} attempts to spend immature coinbase ({confirmations} < {COINBASE_MATURITY} confirmations)", 0

        total_in += utxo.txout.value

    total_out = sum(out.value for out in tx.vout)
    if total_out > total_in:
        return False, f"Outputs ({total_out}) exceed inputs ({total_in})", 0

    fee = total_in - total_out
    return True, "Valid Inputs", fee


def CheckScripts(tx: Transaction, utxo_set: UTXOSet) -> Tuple[bool, str]:
    """Stage 10: Verify digital signatures (Secp256k1, ML-DSA-44, or Hybrid)."""
    if tx.is_coinbase():
        return True, "Coinbase requires no script verification"

    for i, inp in enumerate(tx.vin):
        utxo = utxo_set.get_utxo(inp.prev_txid, inp.prev_vout)
        if utxo is None:
            return False, f"Input {i} UTXO missing for script check"

        prev_script = utxo.txout.script_pubkey
        prev_amount = utxo.txout.value

        if not tx.verify_input_signature(i, prev_script, prev_amount):
            return False, f"Signature verification failed for input {i}"

    return True, "Valid Scripts"
