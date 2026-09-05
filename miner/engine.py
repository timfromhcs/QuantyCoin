"""
QuantyCoin Multi-Threaded Mining Engine
High-Performance Parallel Solo & Pool Miner with Real-Time Hashrate Telemetry
Zero-Mock Implementation
"""

import time
import struct
import threading
from typing import Optional, Callable, Dict, Any, List
from crypto import hash256, compute_merkle_root
from core.transaction import Transaction, TxIn, TxOut
from core.block import Block, BlockHeader
from wallet.rpc_client import WalletRPCClient


import hashlib

class MiningWorker:
    """Individual worker thread searching a slice of the 32-bit nonce space."""
    def __init__(self, worker_id: int, start_nonce: int, nonce_stride: int, header_prefix: bytes, header_suffix: bytes, target: int, on_found: Callable[[int, bytes], None], pow_type: int = 0):
        self.worker_id = worker_id
        self.nonce = start_nonce
        self.nonce_stride = nonce_stride
        self.header_prefix = header_prefix  # 76 bytes (version, prev_block, merkle_root, time, bits)
        self.target = target
        self.on_found = on_found
        self.pow_type = pow_type
        
        self.is_running = True
        self.hashes_computed = 0
        self.last_hash_rate = 0.0

    def run(self) -> None:
        prefix = self.header_prefix
        target = self.target
        stride = self.nonce_stride
        curr_nonce = self.nonce
        pow_type = self.pow_type
        
        while self.is_running and curr_nonce <= 0xFFFFFFFF:
            header = prefix + struct.pack('<I', curr_nonce)
            if pow_type == 1:
                h = hashlib.scrypt(header, salt=b"quantycoin_pow_gp", n=1024, r=1, p=1, maxmem=0, dklen=32)
            else:
                h = hash256(header)
            self.hashes_computed += 1
            
            # Check target (little endian int)
            h_int = int.from_bytes(h[::-1], 'big')
            if h_int <= target:
                self.on_found(curr_nonce, h)
                break
                
            curr_nonce += stride


class MiningEngine:
    """Multi-Threaded Solo Mining Engine for QuantyCoin."""
    def __init__(self, payout_address: str, rpc_host: str = "127.0.0.1", rpc_port: int = 19889, threads: int = 4, pow_type: int = 0):
        self.payout_address = payout_address
        self.rpc_client = WalletRPCClient(rpc_host=rpc_host, rpc_port=rpc_port)
        self.threads = threads
        self.pow_type = pow_type
        
        self.is_mining = False
        self.total_hashes = 0
        self.blocks_mined = 0
        self.start_time = 0.0
        self.current_hashrate = 0.0
        self.history_hashrates: List[Dict[str, Any]] = []
        
        self._workers: List[MiningWorker] = []
        self._worker_threads: List[threading.Thread] = []
        self._mining_loop_thread: Optional[threading.Thread] = None
        self._block_found_event = threading.Event()
        self._winning_nonce: Optional[int] = None
        self._winning_hash: Optional[bytes] = None

    def start(self) -> None:
        """Start mining loop."""
        self.is_mining = True
        self.start_time = time.time()
        self._mining_loop_thread = threading.Thread(target=self._solo_mining_loop, daemon=True)
        self._mining_loop_thread.start()

    def stop(self) -> None:
        """Stop all mining worker threads."""
        self.is_mining = False
        for w in self._workers:
            w.is_running = False
        self._block_found_event.set()

    def _on_block_found(self, nonce: int, block_hash: bytes) -> None:
        self._winning_nonce = nonce
        self._winning_hash = block_hash
        self._block_found_event.set()

    def _solo_mining_loop(self) -> None:
        """Continuously fetch block templates, mine nonces, and submit blocks."""
        while self.is_mining:
            try:
                # 1. Fetch template from node
                tmpl = self.rpc_client.get_block_template(self.pow_type)
                version = tmpl["version"]
                prev_hash = bytes.fromhex(tmpl["previousblockhash"])[::-1]
                height = tmpl["height"]
                bits = int(tmpl["bits"], 16)
                target = int(tmpl["target"], 16)
                
                # 2. Build Coinbase Transaction
                from crypto.bip32_44 import address_to_scriptpubkey
                script_pubkey = address_to_scriptpubkey(self.payout_address)
                
                lane_name = "GP" if self.pow_type == 1 else "SHA"
                cb_msg = f"/QuantyMiner:QTY4/{lane_name}/H:{height}/".encode('utf-8')
                cb_script = bytes([len(cb_msg)]) + cb_msg
                
                coinbase_tx = Transaction(
                    version=1,
                    vin=[TxIn(prev_txid=b'\x00'*32, prev_vout=0xFFFFFFFF, script_sig=cb_script)],
                    vout=[TxOut(value=tmpl["coinbasevalue"], script_pubkey=script_pubkey)],
                    locktime=0
                )
                
                # Mempool transactions
                txs = [coinbase_tx]
                for raw_hex in tmpl["transactions"]:
                    tx, _ = Transaction.deserialize(bytes.fromhex(raw_hex))
                    txs.append(tx)
                    
                # Compute Merkle Root
                merkle_root = compute_merkle_root([tx.txid for tx in txs])
                timestamp = int(time.time())
                
                header_prefix = (
                    struct.pack('<i', version) +
                    prev_hash +
                    merkle_root +
                    struct.pack('<I', timestamp) +
                    struct.pack('<I', bits)
                )
                
                # 3. Launch worker threads
                self._block_found_event.clear()
                self._winning_nonce = None
                self._workers = []
                self._worker_threads = []
                
                for t_idx in range(self.threads):
                    w = MiningWorker(
                        worker_id=t_idx,
                        start_nonce=t_idx,
                        nonce_stride=self.threads,
                        header_prefix=header_prefix,
                        header_suffix=b'',
                        target=target,
                        on_found=self._on_block_found,
                        pow_type=self.pow_type
                    )
                    self._workers.append(w)
                    th = threading.Thread(target=w.run, daemon=True)
                    self._worker_threads.append(th)
                    th.start()
                    
                # 4. Monitor workers & telemetry until found or new template arrives
                t_start = time.time()
                while not self._block_found_event.is_set() and self.is_mining:
                    time.sleep(0.5)
                    # Telemetry calculation
                    elapsed = time.time() - t_start
                    total_worker_hashes = sum(w.hashes_computed for w in self._workers)
                    if elapsed > 0:
                        self.current_hashrate = total_worker_hashes / elapsed
                        
                    # Periodically save hashrate point
                    if len(self.history_hashrates) == 0 or time.time() - self.history_hashrates[-1]["t"] >= 2.0:
                        self.history_hashrates.append({
                            "t": time.time(),
                            "hashrate": round(self.current_hashrate, 2)
                        })
                        if len(self.history_hashrates) > 60:
                            self.history_hashrates.pop(0)
                            
                    # Refresh template every 15s if not found
                    if elapsed > 15.0:
                        break
                        
                # Stop workers for this round
                for w in self._workers:
                    w.is_running = False
                self.total_hashes += sum(w.hashes_computed for w in self._workers)
                
                # 5. If block was solved, construct and submit
                if self._winning_nonce is not None:
                    solved_header = BlockHeader(
                        version=version,
                        prev_block=prev_hash,
                        merkle_root=merkle_root,
                        timestamp=timestamp,
                        bits=bits,
                        nonce=self._winning_nonce
                    )
                    solved_block = Block(header=solved_header, transactions=txs)
                    raw_block_hex = solved_block.serialize().hex()
                    
                    try:
                        res = self.rpc_client.submit_block(raw_block_hex)
                        if res == "accepted":
                            self.blocks_mined += 1
                            print(f"\n>>> [BLOCK MINED & ACCEPTED] Hash: {solved_block.hash_hex} (Height: {height}) <<<")
                    except Exception as e:
                        print(f"Block submission error: {e}")
                        
            except Exception as e:
                time.sleep(2)

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live mining telemetry."""
        return {
            "is_mining": self.is_mining,
            "threads": self.threads,
            "hashrate_hs": round(self.current_hashrate, 2),
            "hashrate_khs": round(self.current_hashrate / 1000, 2),
            "hashrate_mhs": round(self.current_hashrate / 1_000_000, 4),
            "total_hashes": self.total_hashes,
            "blocks_mined": self.blocks_mined,
            "payout_address": self.payout_address,
            "history": self.history_hashrates[-30:]
        }
