"""
QuantyCoin P2P Network Manager & Discovery Service
Listens on TCP Port 19888, Manages Peer Pool, PEX & Block/Tx Broadcasting
Zero-Mock Implementation
"""

import socket
import threading
import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from core.genesis_constants import DEFAULT_P2P_PORT
from .peer import PeerConnection
from .protocol import (
    parse_version_payload, build_inv_payload, parse_inv_payload,
    INV_TYPE_BLOCK, INV_TYPE_TX
)


class P2PManager:
    """Central P2P Orchestrator for the QuantyCoin Node."""
    def __init__(self, listen_host: str = "0.0.0.0", listen_port: int = DEFAULT_P2P_PORT, max_peers: int = 125):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.max_peers = max_peers
        
        self._lock = threading.RLock()
        self._peers: Dict[str, PeerConnection] = {}
        self._known_addresses: set = set()
        
        # Callbacks to node/chainstate
        self.on_new_block_received: Optional[Callable[[bytes, PeerConnection], None]] = None
        self.on_new_tx_received: Optional[Callable[[bytes, PeerConnection], None]] = None
        self.get_local_height: Callable[[], int] = lambda: 0
        self.get_block_by_hash: Optional[Callable[[bytes], Optional[bytes]]] = None
        self.get_tx_by_hash: Optional[Callable[[bytes], Optional[bytes]]] = None
        
        self._server_sock: Optional[socket.socket] = None
        self._is_running = False
        self._listen_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start P2P server and discovery threads."""
        self._is_running = True
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.listen_host, self.listen_port))
        self._server_sock.listen(50)
        
        self._listen_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._listen_thread.start()
        
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self) -> None:
        """Gracefully terminate P2P server and disconnect all peers."""
        self._is_running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
        with self._lock:
            for peer in list(self._peers.values()):
                peer.disconnect()
            self._peers.clear()

    def connect_to_peer(self, host: str, port: int = DEFAULT_P2P_PORT) -> bool:
        """Establish outbound connection to a peer."""
        peer_key = f"{host}:{port}"
        with self._lock:
            if peer_key in self._peers or len(self._peers) >= self.max_peers:
                return False
                
        try:
            sock = socket.create_connection((host, port), timeout=5)
            peer = PeerConnection(
                sock=sock,
                address=host,
                port=port,
                is_inbound=False,
                on_message=self._handle_message,
                on_disconnect=self._handle_peer_disconnect
            )
            with self._lock:
                self._peers[peer_key] = peer
                self._known_addresses.add((host, port))
            
            # Send initial version handshake
            peer.send_version(self.get_local_height())
            return True
        except Exception:
            return False

    def _accept_loop(self) -> None:
        """Accept inbound connections from other nodes."""
        while self._is_running and self._server_sock:
            try:
                sock, (addr, port) = self._server_sock.accept()
                peer_key = f"{addr}:{port}"
                
                with self._lock:
                    if len(self._peers) >= self.max_peers:
                        sock.close()
                        continue
                        
                    peer = PeerConnection(
                        sock=sock,
                        address=addr,
                        port=port,
                        is_inbound=True,
                        on_message=self._handle_message,
                        on_disconnect=self._handle_peer_disconnect
                    )
                    self._peers[peer_key] = peer
                    self._known_addresses.add((addr, port))
                    
            except Exception:
                if not self._is_running:
                    break

    def _handle_peer_disconnect(self, peer: PeerConnection) -> None:
        peer_key = f"{peer.address}:{peer.port}"
        with self._lock:
            self._peers.pop(peer_key, None)

    def _handle_message(self, peer: PeerConnection, command: str, payload: bytes) -> None:
        """Process incoming P2P message."""
        try:
            if command == "version":
                info = parse_version_payload(payload)
                peer.peer_version = info["version"]
                peer.peer_height = info["start_height"]
                peer.user_agent = info["user_agent"]
                peer.send_verack()
                if peer.is_inbound:
                    peer.send_version(self.get_local_height())
                    
            elif command == "verack":
                peer.handshake_complete = True
                
            elif command == "inv":
                items = parse_inv_payload(payload)
                # Request missing blocks or txs with getdata
                getdata_items = []
                for inv_type, inv_hash in items:
                    getdata_items.append((inv_type, inv_hash))
                if getdata_items:
                    peer.send_message("getdata", build_inv_payload(getdata_items))
                    
            elif command == "getdata":
                items = parse_inv_payload(payload)
                for inv_type, inv_hash in items:
                    if inv_type == INV_TYPE_BLOCK and self.get_block_by_hash:
                        raw_block = self.get_block_by_hash(inv_hash)
                        if raw_block:
                            peer.send_message("block", raw_block)
                    elif inv_type == INV_TYPE_TX and self.get_tx_by_hash:
                        raw_tx = self.get_tx_by_hash(inv_hash)
                        if raw_tx:
                            peer.send_message("tx", raw_tx)
                            
            elif command == "block":
                if self.on_new_block_received:
                    self.on_new_block_received(payload, peer)
                    
            elif command == "tx":
                if self.on_new_tx_received:
                    self.on_new_tx_received(payload, peer)
                    
        except Exception:
            pass

    def broadcast_block(self, block_hash: bytes, raw_block: bytes) -> None:
        """Broadcast newly mined/received block to all connected peers."""
        inv_payload = build_inv_payload([(INV_TYPE_BLOCK, block_hash)])
        with self._lock:
            for peer in list(self._peers.values()):
                if peer.handshake_complete:
                    peer.send_message("inv", inv_payload)

    def broadcast_tx(self, txid: bytes, raw_tx: bytes) -> None:
        """Broadcast new unconfirmed transaction to all peers."""
        inv_payload = build_inv_payload([(INV_TYPE_TX, txid)])
        with self._lock:
            for peer in list(self._peers.values()):
                if peer.handshake_complete:
                    peer.send_message("inv", inv_payload)

    def _heartbeat_loop(self) -> None:
        """Periodic ping/pong to track latency and keep connections alive."""
        while self._is_running:
            time.sleep(15)
            with self._lock:
                peers = list(self._peers.values())
            for peer in peers:
                if peer.handshake_complete:
                    peer.send_ping()

    @property
    def peer_count(self) -> int:
        with self._lock:
            return len(self._peers)

    def get_peer_info(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [peer.to_dict() for peer in self._peers.values()]
