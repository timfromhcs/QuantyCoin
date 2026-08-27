"""
QuantyCoin Core - UTXO Set State Machine & Undo Management
Zero-Mock Implementation with Atomic Block Application and Rollback (Reorg Recovery)
"""

import threading
from typing import Dict, Tuple, Optional, List, Set, Any
from .transaction import Transaction, TxOut


class UTXOEntry:
    """Individual Unspent Transaction Output entry."""
    def __init__(self, value: int, script_pubkey: bytes, height: int, is_coinbase: bool = False):
        self.value = value                  # In satoshis
        self.script_pubkey = script_pubkey  # Locking script
        self.height = height                # Block height when created
        self.is_coinbase = is_coinbase      # Whether generated in coinbase

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value / 100_000_000,
            "value_sat": self.value,
            "scriptPubKey": self.script_pubkey.hex(),
            "height": self.height,
            "coinbase": self.is_coinbase
        }


class BlockUndo:
    """Undo data to revert a block application during a chain reorganization."""
    def __init__(self, block_hash: bytes, spent_utxos: Dict[Tuple[bytes, int], UTXOEntry], created_outpoints: Set[Tuple[bytes, int]]):
        self.block_hash = block_hash
        self.spent_utxos = spent_utxos
        self.created_outpoints = created_outpoints


class UTXOSet:
    """In-memory & persistent thread-safe UTXO state database."""
    def __init__(self):
        self._lock = threading.RLock()
        # Map: (txid: bytes, vout: int) -> UTXOEntry
        self._utxos: Dict[Tuple[bytes, int], UTXOEntry] = {}
        # History of block undos: block_hash -> BlockUndo
        self._undo_history: Dict[bytes, BlockUndo] = {}

    def get_utxo(self, txid: bytes, vout: int) -> Optional[UTXOEntry]:
        with self._lock:
            return self._utxos.get((txid, vout))

    def has_utxo(self, txid: bytes, vout: int) -> bool:
        with self._lock:
            return (txid, vout) in self._utxos

    def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Find all UTXOs belonging to a specific address."""
        from crypto.bip32_44 import encode_segwit_address, MAINNET_BECH32_HRP, base58check_encode, MAINNET_PUBKEY_HASH_PREFIX
        results = []
        with self._lock:
            for (txid, vout), entry in self._utxos.items():
                out = TxOut(entry.value, entry.script_pubkey)
                if out.get_address() == address:
                    results.append({
                        "txid": txid[::-1].hex(),
                        "vout": vout,
                        "value": entry.value / 100_000_000,
                        "value_sat": entry.value,
                        "scriptPubKey": entry.script_pubkey.hex(),
                        "height": entry.height,
                        "coinbase": entry.is_coinbase
                    })
        return results

    def get_address_balance(self, address: str) -> Tuple[int, int]:
        """Returns (balance_sat, utxo_count) for an address."""
        utxos = self.get_address_utxos(address)
        tot_sat = sum(u["value_sat"] for u in utxos)
        return tot_sat, len(utxos)

    def apply_block(self, block_hash: bytes, height: int, transactions: List[Transaction]) -> BlockUndo:
        """
        Atomically apply all transactions in a block to the UTXO set.
        Returns BlockUndo data to permit rollback on chain split / reorg.
        """
        with self._lock:
            spent_utxos: Dict[Tuple[bytes, int], UTXOEntry] = {}
            created_outpoints: Set[Tuple[bytes, int]] = set()
            
            # 1. Spend inputs (except coinbase)
            for tx in transactions:
                if not tx.is_coinbase():
                    for inp in tx.vin:
                        outpoint = (inp.prev_txid, inp.prev_vout)
                        if outpoint not in self._utxos:
                            # Rollback partial block application on error
                            self._rollback_partial(spent_utxos, created_outpoints)
                            raise ValueError(f"Missing UTXO for input {inp.prev_txid[::-1].hex()}:{inp.prev_vout}")
                        spent_entry = self._utxos.pop(outpoint)
                        spent_utxos[outpoint] = spent_entry
                        
                # 2. Add outputs
                txid = tx.txid
                is_cb = tx.is_coinbase()
                for vout_idx, out in enumerate(tx.vout):
                    outpoint = (txid, vout_idx)
                    entry = UTXOEntry(
                        value=out.value,
                        script_pubkey=out.script_pubkey,
                        height=height,
                        is_coinbase=is_cb
                    )
                    self._utxos[outpoint] = entry
                    created_outpoints.add(outpoint)
                    
            undo = BlockUndo(block_hash, spent_utxos, created_outpoints)
            self._undo_history[block_hash] = undo
            return undo

    def revert_block(self, block_hash: bytes) -> None:
        """
        Roll back a block from the UTXO set using its undo data.
        Essential for seamless chain reorgs.
        """
        with self._lock:
            if block_hash not in self._undo_history:
                raise ValueError(f"No undo data available for block {block_hash[::-1].hex()}")
            undo = self._undo_history.pop(block_hash)
            
            # Remove outputs created by the block
            for outpoint in undo.created_outpoints:
                self._utxos.pop(outpoint, None)
                
            # Restore outputs spent by the block
            for outpoint, entry in undo.spent_utxos.items():
                self._utxos[outpoint] = entry

    def _rollback_partial(self, spent: Dict[Tuple[bytes, int], UTXOEntry], created: Set[Tuple[bytes, int]]) -> None:
        for outpoint in created:
            self._utxos.pop(outpoint, None)
        for outpoint, entry in spent.items():
            self._utxos[outpoint] = entry

    @property
    def total_utxo_count(self) -> int:
        with self._lock:
            return len(self._utxos)

    @property
    def total_circulation(self) -> int:
        """Returns total satoshis in circulation across the UTXO set."""
        with self._lock:
            return sum(entry.value for entry in self._utxos.values())
