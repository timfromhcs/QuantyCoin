"""
QuantyCoin Core Package
Zero-Mock Consensus, State Machine, Block & Transaction Primitives
"""

from .transaction import Transaction, TxIn, TxOut
from .block import Block, BlockHeader
from .utxo import UTXOSet, UTXOEntry, BlockUndo
from .mempool import Mempool, MempoolEntry
from .consensus import (
    get_block_subsidy, calculate_next_work_required_lwma,
    target_to_bits, bits_to_target, POW_LIMIT_BITS, POW_LIMIT_TARGET
)
from .genesis_constants import (
    MAGIC_BYTES, DEFAULT_P2P_PORT, DEFAULT_RPC_PORT, DEFAULT_STRATUM_PORT,
    GENESIS_HASH, GENESIS_MERKLE_ROOT, GENESIS_TIMESTAMP, GENESIS_NONCE,
    GENESIS_BITS, GENESIS_COINBASE_PAYOUT_ADDRESS, GENESIS_BLOCK_REWARD,
    TARGET_BLOCK_TIME, SUBSIDY_HALVING_INTERVAL
)

__all__ = [
    "Transaction", "TxIn", "TxOut",
    "Block", "BlockHeader",
    "UTXOSet", "UTXOEntry", "BlockUndo",
    "Mempool", "MempoolEntry",
    "get_block_subsidy", "calculate_next_work_required_lwma",
    "target_to_bits", "bits_to_target", "POW_LIMIT_BITS", "POW_LIMIT_TARGET",
    "MAGIC_BYTES", "DEFAULT_P2P_PORT", "DEFAULT_RPC_PORT", "DEFAULT_STRATUM_PORT",
    "GENESIS_HASH", "GENESIS_MERKLE_ROOT", "GENESIS_TIMESTAMP", "GENESIS_NONCE",
    "GENESIS_BITS", "GENESIS_COINBASE_PAYOUT_ADDRESS", "GENESIS_BLOCK_REWARD",
    "TARGET_BLOCK_TIME", "SUBSIDY_HALVING_INTERVAL"
]
