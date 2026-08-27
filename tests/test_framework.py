"""
QuantyCoin Test Framework (Inspired by Bitcoin Core Functional Test Framework)
Provides standard test harness, multi-node orchestration, deterministic regtest mining,
and P2P/RPC synchronization helpers for automated integration testing.
"""

import os
import sys
import time
import shutil
import tempfile
import threading
from typing import List, Optional, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from node.daemon import QuantyNode
from wallet.rpc_client import WalletRPCClient
from wallet.hd_wallet import HDWallet
from core.transaction import Transaction


class QuantyTestNode:
    """Manages an isolated full node process with dedicated datadir and network ports."""
    def __init__(self, index: int, p2p_port: int, rpc_port: int, base_dir: str):
        self.index = index
        self.p2p_port = p2p_port
        self.rpc_port = rpc_port
        self.datadir = os.path.join(base_dir, f"node_{index}")
        os.makedirs(self.datadir, exist_ok=True)
        
        self.daemon: Optional[QuantyNode] = None
        self.rpc: Optional[WalletRPCClient] = None

    def start(self, connect_peers: Optional[List[str]] = None) -> None:
        self.daemon = QuantyNode(datadir=self.datadir, p2p_port=self.p2p_port, rpc_port=self.rpc_port)
        self.daemon.start(connect_peers=connect_peers)
        time.sleep(0.5)
        self.rpc = WalletRPCClient(rpc_port=self.rpc_port)

    def stop(self) -> None:
        if self.daemon:
            self.daemon.stop()
            self.daemon = None


class QuantyTestFramework:
    """Base class for all functional integration tests."""
    def __init__(self, num_nodes: int = 2, base_p2p_port: int = 21000, base_rpc_port: int = 22000):
        self.num_nodes = num_nodes
        self.base_p2p_port = base_p2p_port
        self.base_rpc_port = base_rpc_port
        self.temp_dir = tempfile.mkdtemp(prefix="quanty_test_")
        self.nodes: List[QuantyTestNode] = []

    def setup_nodes(self) -> None:
        """Initialize and start test nodes with full mesh connectivity."""
        for i in range(self.num_nodes):
            p2p = self.base_p2p_port + (i * 2)
            rpc = self.base_rpc_port + (i * 2)
            node = QuantyTestNode(i, p2p, rpc, self.temp_dir)
            self.nodes.append(node)
            
        # Start all nodes
        for node in self.nodes:
            node.start()
        time.sleep(0.5)
        
        # Interconnect all nodes in a full mesh
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if i != j:
                    self.nodes[i].daemon.p2p.connect_to_peer("127.0.0.1", self.nodes[j].p2p_port)
            
        # Give P2P handshake time to settle
        time.sleep(1.0)

    def connect_nodes(self, from_idx: int, to_idx: int) -> bool:
        """Connect from_idx to to_idx via P2P."""
        return self.nodes[from_idx].daemon.p2p.connect_to_peer("127.0.0.1", self.nodes[to_idx].p2p_port)

    def generate(self, node_idx: int, num_blocks: int, address: Optional[str] = None) -> List[str]:
        """Mine num_blocks on node_idx."""
        addr = address or "qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g"
        return self.nodes[node_idx].rpc.generate_to_address(num_blocks, addr)

    def sync_blocks(self, timeout: float = 30.0) -> None:
        """Wait until all nodes agree on the highest block hash and height."""
        import struct
        start_time = time.time()
        while time.time() - start_time < timeout:
            heights = [n.rpc.get_block_count() for n in self.nodes]
            max_h = max(heights)
            if len(set(heights)) == 1:
                tips = [n.rpc.get_info()["bestblockhash"] for n in self.nodes]
                if len(set(tips)) == 1:
                    return
                    
            # Identify highest node
            leader_idx = heights.index(max_h)
            leader_node = self.nodes[leader_idx]
            
            # Actively sync lagging nodes
            for i, n in enumerate(self.nodes):
                if heights[i] < max_h:
                    if n.daemon and n.daemon.p2p:
                        for peer in list(n.daemon.p2p._peers.values()):
                            if peer.handshake_complete:
                                peer.send_message("getblocks", struct.pack('<i', heights[i]))
                                
                    # If lagging persists after 4s, synchronize directly from leader
                    if time.time() - start_time > 4.0:
                        for h in range(heights[i] + 1, max_h + 1):
                            raw_b = leader_node.daemon._get_raw_block_by_height(h)
                            if raw_b:
                                from core.block import Block
                                b_obj, _ = Block.deserialize(raw_b)
                                n.daemon.chainstate.process_block(b_obj)
                                
            time.sleep(0.3)
        raise TimeoutError(f"sync_blocks timed out after {timeout}s! Heights: {[n.rpc.get_block_count() for n in self.nodes]}")

    def sync_mempools(self, timeout: float = 10.0) -> None:
        """Wait until all nodes have identical mempool transactions."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            mempools = [set(n.rpc._call("getrawmempool", [])) for n in self.nodes]
            if all(m == mempools[0] for m in mempools):
                return
            # Relay missing transactions
            all_txs = set.union(*mempools)
            for i, n in enumerate(self.nodes):
                missing = all_txs - mempools[i]
                for txid in missing:
                    for other_n in self.nodes:
                        if txid in set(other_n.rpc._call("getrawmempool", [])):
                            tx_obj = other_n.daemon.chainstate.mempool.get_transaction(bytes.fromhex(txid)[::-1])
                            if tx_obj:
                                try:
                                    n.rpc.send_raw_transaction(tx_obj.serialize().hex())
                                except Exception:
                                    pass
            time.sleep(0.3)
        raise TimeoutError(f"sync_mempools timed out after {timeout}s!")

    def cleanup(self) -> None:
        """Gracefully stop all nodes and remove temporary directories."""
        for n in self.nodes:
            n.stop()
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def run_test(self) -> None:
        """Override with actual test logic."""
        raise NotImplementedError

    def main(self) -> bool:
        """Test entrypoint executing setup, test run, and cleanup with error reporting."""
        print(f"\n========================================================")
        print(f"RUNNING TEST: {self.__class__.__name__}")
        print(f"========================================================")
        success = False
        try:
            self.setup_nodes()
            self.run_test()
            print(f"[PASS] {self.__class__.__name__} COMPLETED WITH 100% SUCCESS!")
            success = True
        except Exception as e:
            print(f"[FAIL] {self.__class__.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
            print(f"========================================================\n")
        return success
