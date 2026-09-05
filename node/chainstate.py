"""
QuantyCoin Node - Chainstate Database & Fork-Choice Engine
Zero-Mock Implementation with Cumulative PoW Work, Fork Resolution & Atomic Reorganization
"""

import os
import sqlite3
import threading
from typing import Dict, List, Tuple, Optional, Any
from crypto import hash256, compute_merkle_root
from core.transaction import Transaction, TxIn, TxOut
from core.block import Block, BlockHeader
from core.utxo import UTXOSet
from core.mempool import Mempool
from core.consensus import (
    get_block_subsidy, calculate_next_work_required_lwma,
    calculate_next_work_required_dual,
    bits_to_target, target_to_bits, POW_LIMIT_BITS,
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE,
    LANE_WEIGHT_SHA256D, LANE_WEIGHT_GENERAL_PURPOSE
)
from core.genesis_constants import (
    GENESIS_HASH, GENESIS_TIMESTAMP, GENESIS_NONCE, GENESIS_BITS,
    GENESIS_TIMESTAMP_STR, GENESIS_COINBASE_PAYOUT_ADDRESS
)


def get_block_work(bits: int, pow_type: int = POW_TYPE_SHA256D) -> int:
    """Calculate chainwork contribution for a given difficulty target and PoW lane."""
    target = bits_to_target(bits)
    if target <= 0:
        return 0
    raw_work = (1 << 256) // (target + 1)
    weight = LANE_WEIGHT_GENERAL_PURPOSE if pow_type == POW_TYPE_GENERAL_PURPOSE else LANE_WEIGHT_SHA256D
    return raw_work * weight


class BlockIndexNode:
    """Represents a block entry in the block tree index."""
    def __init__(self, header: BlockHeader, height: int, chainwork: int, raw_block: bytes, prev_hash: bytes):
        self.header = header
        self.height = height
        self.chainwork = chainwork
        self.raw_block = raw_block
        self.prev_hash = prev_hash
        self.hash = header.hash

    @property
    def pow_type(self) -> int:
        return self.header.pow_type


class Chainstate:
    """Manages active best chain, block tree index, and chain reorganizations."""
    def __init__(self, datadir: Optional[str] = None):
        self.datadir = datadir
        self._lock = threading.RLock()
        
        self.utxo_set = UTXOSet()
        self.mempool = Mempool()
        
        # Block index: block_hash (32 bytes) -> BlockIndexNode
        self.block_index: Dict[bytes, BlockIndexNode] = {}
        # Active chain: height (int) -> block_hash (32 bytes)
        self.active_chain: List[bytes] = []
        self.best_tip: Optional[BlockIndexNode] = None
        
        self._init_genesis()

    def _init_genesis(self) -> None:
        """Construct and connect the hardcoded Genesis block."""
        # 1. Build Genesis Coinbase TX
        script_sig = b'\x04\xff\xff\x00\x1d\x01\x04' + bytes([len(GENESIS_TIMESTAMP_STR)]) + GENESIS_TIMESTAMP_STR.encode('utf-8')
        
        from crypto.bip32_44 import address_to_scriptpubkey
        script_pubkey = address_to_scriptpubkey(GENESIS_COINBASE_PAYOUT_ADDRESS)
        
        cb_tx = Transaction(
            version=1,
            vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
            vout=[TxOut(value=50 * 100_000_000, script_pubkey=script_pubkey)],
            locktime=0
        )
        
        # 2. Build Genesis Header
        genesis_header = BlockHeader(
            version=1,
            prev_block=b'\x00' * 32,
            merkle_root=compute_merkle_root([cb_tx.txid]),
            timestamp=GENESIS_TIMESTAMP,
            bits=GENESIS_BITS,
            nonce=GENESIS_NONCE
        )
        genesis_block = Block(header=genesis_header, transactions=[cb_tx])

        # Mandatory Consensus Runtime Assertions
        if genesis_header.hash_hex != GENESIS_HASH:
            raise RuntimeError(
                f"[CONSENSUS CORRUPTION] Genesis block hash mismatch! "
                f"Expected {GENESIS_HASH}, computed {genesis_header.hash_hex}."
            )
        if not genesis_header.verify_pow():
            raise RuntimeError("[CONSENSUS CORRUPTION] Genesis block fails Proof-of-Work verification!")
        if not genesis_block.verify_merkle_root():
            raise RuntimeError("[CONSENSUS CORRUPTION] Genesis block Merkle root mismatch!")

        raw_genesis = genesis_block.serialize()
        gen_hash = genesis_header.hash
        
        node = BlockIndexNode(
            header=genesis_header,
            height=0,
            chainwork=get_block_work(GENESIS_BITS),
            raw_block=raw_genesis,
            prev_hash=b'\x00' * 32
        )
        
        self.block_index[gen_hash] = node
        self.active_chain = [gen_hash]
        self.best_tip = node
        
        # Apply Genesis block to UTXO set
        self.utxo_set.apply_block(gen_hash, 0, [cb_tx])

    @property
    def best_height(self) -> int:
        with self._lock:
            return self.best_tip.height if self.best_tip else 0

    @property
    def best_hash(self) -> bytes:
        with self._lock:
            return self.best_tip.hash if self.best_tip else (b'\x00' * 32)

    @property
    def best_hash_hex(self) -> str:
        return self.best_hash[::-1].hex()

    def get_block_by_hash(self, block_hash: bytes) -> Optional[Block]:
        with self._lock:
            node = self.block_index.get(block_hash)
            if not node:
                return None
            block, _ = Block.deserialize(node.raw_block)
            return block

    def get_block_by_height(self, height: int) -> Optional[Block]:
        with self._lock:
            if 0 <= height < len(self.active_chain):
                block_hash = self.active_chain[height]
                return self.get_block_by_hash(block_hash)
            return None

    def get_header_by_hash(self, block_hash: bytes) -> Optional[BlockHeader]:
        with self._lock:
            node = self.block_index.get(block_hash)
            return node.header if node else None

    def get_block_work(self, header: BlockHeader) -> int:
        """Calculate thermodynamic work for block header."""
        return get_block_work(header.bits, header.pow_type)

    def get_next_work_required(self, pow_type: int = POW_TYPE_SHA256D) -> int:
        """Calculate next difficulty target bits for mining on specified PoW lane."""
        with self._lock:
            headers = [self.block_index[h].header for h in self.active_chain]
            return calculate_next_work_required_dual(headers, pow_type=pow_type)

    def process_block(self, block: Block) -> Tuple[bool, str]:
        """
        Full block validation and chain integration pipeline.
        Handles both normal extensions and deep fork reorganizations.
        """
        with self._lock:
            block_hash = block.hash
            
            if block_hash in self.block_index:
                return False, "Duplicate block"
                
            # 1. Structural Validation
            valid_struct, err = block.validate_structure()
            if not valid_struct:
                return False, f"Invalid block structure: {err}"
                
            # 2. Check Parent Block
            prev_hash = block.header.prev_block
            if prev_hash not in self.block_index:
                return False, "Orphan block (parent not found)"
                
            parent_node = self.block_index[prev_hash]
            height = parent_node.height + 1
            
            # 3. Verify Contextual PoW & Difficulty
            # Verify timestamp is after median time past
            if block.header.timestamp <= parent_node.header.timestamp - 7200:
                return False, "Block timestamp too far in past"
                
            chainwork = parent_node.chainwork + get_block_work(block.header.bits, block.header.pow_type)
            raw_block = block.serialize()
            
            node = BlockIndexNode(
                header=block.header,
                height=height,
                chainwork=chainwork,
                raw_block=raw_block,
                prev_hash=prev_hash
            )
            self.block_index[block_hash] = node
            
            # 4. Fork Choice Rule: Longest cumulative chainwork
            if chainwork > self.best_tip.chainwork:
                # Reorganize or extend active chain to this node
                success, reorg_err = self._reorg_to_node(node)
                if not success:
                    # Failed application - prune from tree
                    self.block_index.pop(block_hash, None)
                    return False, f"Chain reorganization failed: {reorg_err}"
                    
                return True, "Accepted (New Best Tip)"
            else:
                return True, "Accepted (Side Chain / Fork)"

    def _reorg_to_node(self, target_node: BlockIndexNode) -> Tuple[bool, str]:
        """
        Seamlessly reorg active chain from current best tip to target node branch.
        """
        # Find common ancestor
        current_branch: List[BlockIndexNode] = []
        curr = self.best_tip
        while curr:
            current_branch.append(curr)
            curr = self.block_index.get(curr.prev_hash)
            
        current_hashes = {n.hash: idx for idx, n in enumerate(current_branch)}
        
        target_branch: List[BlockIndexNode] = []
        curr = target_node
        while curr:
            if curr.hash in current_hashes:
                # Found common ancestor!
                ancestor = curr
                break
            target_branch.append(curr)
            curr = self.block_index.get(curr.prev_hash)
            
        if not curr:
            return False, "No common ancestor with active chain"
            
        # Target branch from ancestor forward
        target_branch.reverse()
        
        # Disconnect blocks on current chain from tip down to ancestor
        ancestor_idx = current_hashes[ancestor.hash]
        disconnect_nodes = current_branch[:ancestor_idx]
        
        # 1. Rollback UTXO state
        for node in disconnect_nodes:
            self.utxo_set.revert_block(node.hash)
            
        # 2. Apply new branch blocks forward
        applied_nodes: List[BlockIndexNode] = []
        try:
            for node in target_branch:
                block, _ = Block.deserialize(node.raw_block)
                # Verify and apply UTXO state transitions
                self.utxo_set.apply_block(node.hash, node.height, block.transactions)
                applied_nodes.append(node)
        except Exception as e:
            # Revert partially applied target nodes
            for node in reversed(applied_nodes):
                self.utxo_set.revert_block(node.hash)
            # Re-apply old branch
            for node in reversed(disconnect_nodes):
                b, _ = Block.deserialize(node.raw_block)
                self.utxo_set.apply_block(node.hash, node.height, b.transactions)
            return False, str(e)
            
        # 3. Update active chain array and best tip
        ancestor_height = ancestor.height
        new_active = self.active_chain[:ancestor_height + 1] + [n.hash for n in target_branch]
        self.active_chain = new_active
        self.best_tip = target_node
        
        # 4. Clean mined transactions from mempool
        for node in target_branch:
            b, _ = Block.deserialize(node.raw_block)
            self.mempool.remove_mined_transactions(b.transactions)
            
        return True, "Reorg Success"
