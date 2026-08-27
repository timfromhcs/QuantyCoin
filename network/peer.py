"""
QuantyCoin Peer Connection & Wire Stream Handler
Thread-Safe TCP Socket Communication & Heartbeat Telemetry
"""

import socket
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from crypto import hash256
from core.genesis_constants import MAGIC_BYTES
from .protocol import (
    HEADER_LENGTH, COMMAND_LENGTH,
    create_message, parse_header,
    build_version_payload, parse_version_payload,
    build_ping_payload, parse_ping_payload
)


class PeerConnection:
    """Manages an individual bidirectional TCP connection with a remote peer."""
    def __init__(self, sock: socket.socket, address: str, port: int, is_inbound: bool, on_message: Callable[['PeerConnection', str, bytes], None], on_disconnect: Callable[['PeerConnection'], None]):
        self.sock = sock
        self.address = address
        self.port = port
        self.is_inbound = is_inbound
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        
        self.is_connected = True
        self.handshake_complete = False
        self.peer_version: Optional[int] = None
        self.peer_height: int = 0
        self.user_agent: str = ""
        self.latency_ms: float = 0.0
        self.last_ping_time: float = 0.0
        self.last_seen: float = time.time()
        
        self._send_lock = threading.Lock()
        self._recv_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._recv_thread.start()

    def send_message(self, command: str, payload: bytes = b'') -> bool:
        """Send framed wire message to the peer."""
        if not self.is_connected:
            return False
        try:
            msg = create_message(command, payload)
            with self._send_lock:
                self.sock.sendall(msg)
            return True
        except Exception:
            self.disconnect()
            return False

    def send_version(self, local_height: int) -> None:
        payload = build_version_payload(best_height=local_height)
        self.send_message("version", payload)

    def send_verack(self) -> None:
        self.send_message("verack", b'')

    def send_ping(self) -> None:
        self.last_ping_time = time.time()
        nonce = int(self.last_ping_time * 1000) & 0xFFFFFFFFFFFFFFFF
        self.send_message("ping", build_ping_payload(nonce))

    def _read_exact(self, num_bytes: int) -> Optional[bytes]:
        buf = bytearray()
        while len(buf) < num_bytes:
            try:
                chunk = self.sock.recv(num_bytes - len(buf))
                if not chunk:
                    return None
                buf.extend(chunk)
            except Exception:
                return None
        return bytes(buf)

    def _read_loop(self) -> None:
        """Continuously read framing headers and dispatch messages."""
        while self.is_connected:
            try:
                # 1. Read 24-byte header
                header_bytes = self._read_exact(HEADER_LENGTH)
                if not header_bytes:
                    break
                    
                magic, command, payload_len, checksum = parse_header(header_bytes)
                
                # Verify magic bytes
                if magic != MAGIC_BYTES:
                    # Invalid magic - disconnect immediately
                    break
                    
                if payload_len > 32 * 1024 * 1024 + 1000: # Max 32MB payload limit
                    break
                    
                # 2. Read payload
                payload = self._read_exact(payload_len) if payload_len > 0 else b''
                if payload is None:
                    break
                    
                # Verify checksum
                if hash256(payload)[:4] != checksum:
                    break
                    
                self.last_seen = time.time()
                
                # Handle ping/pong directly
                if command == "ping":
                    self.send_message("pong", payload)
                elif command == "pong":
                    if self.last_ping_time > 0:
                        self.latency_ms = (time.time() - self.last_ping_time) * 1000
                else:
                    self.on_message(self, command, payload)
                    
            except Exception:
                break
                
        self.disconnect()

    def disconnect(self) -> None:
        if self.is_connected:
            self.is_connected = False
            try:
                self.sock.close()
            except Exception:
                pass
            self.on_disconnect(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "addr": f"{self.address}:{self.port}",
            "inbound": self.is_inbound,
            "subver": self.user_agent,
            "startingheight": self.peer_height,
            "pingtime": round(self.latency_ms, 2),
            "lastrecv": int(self.last_seen),
            "handshake": self.handshake_complete
        }
