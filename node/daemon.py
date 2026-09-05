"""
QuantyCoin Full Node Daemon
Integrates Chainstate, Mempool, P2P Wire Network & RPC/REST Server into a Unified Daemon
"""

import os
import sys
import time
import signal
import threading
from typing import Optional, List
from core.genesis_constants import DEFAULT_P2P_PORT, DEFAULT_RPC_PORT
from core.block import Block
from core.transaction import Transaction
from network.p2p_server import P2PManager
from network.peer import PeerConnection
from .chainstate import Chainstate
from .rpc_server import QuantyRPCServer


class QuantyNode:
    """Production Full Node Daemon for the QuantyCoin Layer-1 Ecosystem."""
    def __init__(self, datadir: Optional[str] = None, p2p_port: int = DEFAULT_P2P_PORT, rpc_port: int = DEFAULT_RPC_PORT, bind_ip: str = "0.0.0.0"):
        self.datadir = datadir or os.path.expanduser("~/.quantycoin")
        os.makedirs(self.datadir, exist_ok=True)
        
        self.p2p_port = p2p_port
        self.rpc_port = rpc_port
        self.bind_ip = bind_ip
        
        self.chainstate = Chainstate(datadir=self.datadir)
        self.p2p = P2PManager(listen_host=bind_ip, listen_port=p2p_port)
        self.rpc = QuantyRPCServer(chainstate=self.chainstate, p2p_manager=self.p2p, host=bind_ip, port=rpc_port)
        
        # Link callbacks
        self.p2p.get_local_height = lambda: self.chainstate.best_height
        self.p2p.get_block_by_hash = self._get_raw_block_by_hash
        self.p2p.get_block_by_height = self._get_raw_block_by_height
        self.p2p.get_tx_by_hash = self._get_raw_tx_by_hash
        self.p2p.on_new_block_received = self._on_p2p_block
        self.p2p.on_new_tx_received = self._on_p2p_tx
        
        self.is_running = False

    def _get_raw_block_by_hash(self, block_hash: bytes) -> Optional[bytes]:
        b = self.chainstate.get_block_by_hash(block_hash)
        return b.serialize() if b else None

    def _get_raw_block_by_height(self, height: int) -> Optional[bytes]:
        b = self.chainstate.get_block_by_height(height)
        return b.serialize() if b else None

    def _get_raw_tx_by_hash(self, txid: bytes) -> Optional[bytes]:
        tx = self.chainstate.mempool.get_transaction(txid)
        return tx.serialize() if tx else None

    def _on_p2p_block(self, raw_payload: bytes, peer: PeerConnection) -> None:
        try:
            block, _ = Block.deserialize(raw_payload)
            accepted, reason = self.chainstate.process_block(block)
            if accepted:
                # Relay to other peers
                self.p2p.broadcast_block(block.hash, raw_payload)
        except Exception:
            pass

    def _on_p2p_tx(self, raw_payload: bytes, peer: PeerConnection) -> None:
        try:
            tx, _ = Transaction.deserialize(raw_payload)
            accepted, reason = self.chainstate.mempool.add_transaction(tx, self.chainstate.utxo_set)
            if accepted:
                self.p2p.broadcast_tx(tx.txid, raw_payload)
        except Exception:
            pass

    def start(self, connect_peers: Optional[List[str]] = None) -> None:
        """Start all node services."""
        self.is_running = True
        print(f"Starting QuantyCoin Node (QTY4 / 4.0.0) on P2P:{self.p2p_port} RPC:{self.rpc_port}...")
        self.p2p.start()
        self.rpc.start()
        print(f"Genesis Hash: {self.chainstate.best_hash_hex}")
        print(f"Current Height: {self.chainstate.best_height}")
        
        if connect_peers:
            for peer_str in connect_peers:
                parts = peer_str.split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else DEFAULT_P2P_PORT
                self.p2p.connect_to_peer(host, port)

    def stop(self) -> None:
        """Gracefully stop node."""
        if self.is_running:
            self.is_running = False
            print("Stopping QuantyCoin Node...")
            self.rpc.stop()
            self.p2p.stop()
            print("Node stopped.")


def run_node_cli():
    import argparse
    parser = argparse.ArgumentParser(description="QuantyCoin Full Node Daemon (quantyd)")
    parser.add_argument("--datadir", type=str, default=None, help="Directory for blockchain data")
    parser.add_argument("--port", type=int, default=DEFAULT_P2P_PORT, help="P2P network port")
    parser.add_argument("--rpcport", type=int, default=DEFAULT_RPC_PORT, help="JSON-RPC server port")
    parser.add_argument("--connect", type=str, action="append", help="Connect to peer node (ip:port)")
    args = parser.parse_args()
    
    node = QuantyNode(datadir=args.datadir, p2p_port=args.port, rpc_port=args.rpcport)
    node.start(connect_peers=args.connect)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()


main = run_node_cli

if __name__ == "__main__":
    main()
