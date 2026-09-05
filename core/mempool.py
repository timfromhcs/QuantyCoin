"""
QuantyCoin Core - Memory Pool (Mempool) Management
Thread-Safe Transaction Queue, Conflict Resolution & Double-Spend Rejection
"""

import threading
import time
from typing import Dict, Set, Tuple, List, Optional, Any
from .transaction import Transaction
from .utxo import UTXOSet


class MempoolEntry:
    """Entry stored in the mempool."""
    def __init__(self, tx: Transaction, fee_sat: int, entry_time: float):
        self.tx = tx
        self.fee_sat = fee_sat
        self.entry_time = entry_time
        self.size = len(tx.serialize(include_witness=True))
        self.fee_rate = fee_sat / max(self.size, 1)  # Satoshis per byte

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.tx.txid_hex,
            "wtxid": self.tx.wtxid_hex,
            "fee": self.fee_sat / 100_000_000,
            "fee_sat": self.fee_sat,
            "fee_rate": self.fee_rate,
            "size": self.size,
            "time": int(self.entry_time)
        }


class Mempool:
    """Thread-safe QuantyCoin Mempool."""
    def __init__(self, max_size_bytes: int = 300 * 1024 * 1024):
        self._lock = threading.RLock()
        self.max_size_bytes = max_size_bytes
        # Map txid (32 bytes) -> MempoolEntry
        self._entries: Dict[bytes, MempoolEntry] = {}
        # Map outpoint (txid: bytes, vout: int) -> spending txid (32 bytes)
        self._spent_outpoints: Dict[Tuple[bytes, int], bytes] = {}

    def add_transaction(self, tx: Transaction, utxo_set: UTXOSet) -> Tuple[bool, str]:
        """
        Validate and add transaction to the mempool.
        Enforces double-spend rejection and cryptographic signature checks.
        """
        with self._lock:
            txid = tx.txid
            
            if txid in self._entries:
                return False, "Transaction already in mempool"
                
            if tx.is_coinbase():
                return False, "Coinbase transaction cannot be accepted to mempool"
                
            if not tx.vin or not tx.vout:
                return False, "Transaction must have at least 1 input and 1 output"
                
            # Check for intra-mempool double spends and UTXO availability
            total_in = 0
            for i, inp in enumerate(tx.vin):
                outpoint = (inp.prev_txid, inp.prev_vout)
                
                # Check conflict with existing mempool transaction
                if outpoint in self._spent_outpoints:
                    conflicting_txid = self._spent_outpoints[outpoint]
                    return False, f"Double spend conflict with mempool transaction {conflicting_txid[::-1].hex()}"
                    
                # Check UTXO set
                utxo = utxo_set.get_utxo(inp.prev_txid, inp.prev_vout)
                if not utxo:
                    return False, f"Missing UTXO for input {inp.prev_txid[::-1].hex()}:{inp.prev_vout}"
                    
                # Verify cryptographic signature
                if not tx.verify_input_signature(i, utxo.script_pubkey, utxo.value):
                    return False, f"Invalid signature on input {i}"
                    
                total_in += utxo.value
                
            total_out = sum(out.value for out in tx.vout)
            if total_out > total_in:
                return False, f"Total outputs ({total_out}) exceed total inputs ({total_in})"
                
            fee = total_in - total_out
            if fee < 0:
                return False, "Negative transaction fee"
                
            # Register in mempool
            entry = MempoolEntry(tx=tx, fee_sat=fee, entry_time=time.time())
            self._entries[txid] = entry
            for inp in tx.vin:
                self._spent_outpoints[(inp.prev_txid, inp.prev_vout)] = txid
                
            return True, "Accepted"

    def remove_transaction(self, txid: bytes) -> None:
        with self._lock:
            if txid in self._entries:
                entry = self._entries.pop(txid)
                for inp in entry.tx.vin:
                    self._spent_outpoints.pop((inp.prev_txid, inp.prev_vout), None)

    def remove_mined_transactions(self, block_txs: List[Transaction]) -> None:
        """Remove transactions included in a newly mined/connected block."""
        with self._lock:
            for tx in block_txs:
                self.remove_transaction(tx.txid)

    def get_transaction(self, txid: bytes) -> Optional[Transaction]:
        with self._lock:
            entry = self._entries.get(txid)
            return entry.tx if entry else None

    def has_transaction(self, txid: bytes) -> bool:
        with self._lock:
            return txid in self._entries

    def get_sorted_transactions(self) -> List[Transaction]:
        """Return transactions sorted by highest fee rate first."""
        with self._lock:
            sorted_entries = sorted(
                self._entries.values(),
                key=lambda e: e.fee_rate,
                reverse=True
            )
            return [e.tx for e in sorted_entries]

    def get_info(self) -> Dict[str, Any]:
        with self._lock:
            tot_bytes = sum(e.size for e in self._entries.values())
            tot_fees = sum(e.fee_sat for e in self._entries.values())
            return {
                "size": len(self._entries),
                "bytes": tot_bytes,
                "total_fee": tot_fees / 100_000_000,
                "total_fee_sat": tot_fees
            }

    def get_all_txids(self) -> List[str]:
        with self._lock:
            return [txid[::-1].hex() for txid in self._entries.keys()]
