"""
QuantyCoin Network Wire Protocol
Binary Framing, Header Encoding, Checksum Validation & Message Definitions
Zero-Mock Implementation (TCP Wire Protocol on Port 19444)
"""

import struct
import time
from typing import List, Tuple, Dict, Any, Optional
from crypto import hash256
from core.genesis_constants import MAGIC_BYTES

# Wire constants
COMMAND_LENGTH = 12
HEADER_LENGTH = 4 + 12 + 4 + 4  # 24 bytes

# Inventory types
INV_TYPE_TX = 1
INV_TYPE_BLOCK = 2


def create_message(command: str, payload: bytes) -> bytes:
    """
    Format complete binary P2P wire frame:
    [4B Magic Bytes][12B Command String][4B Payload Length][4B Checksum][Payload]
    """
    cmd_bytes = command.encode('ascii')
    if len(cmd_bytes) > COMMAND_LENGTH:
        raise ValueError(f"Command '{command}' exceeds max 12 ASCII characters")
    cmd_padded = cmd_bytes + (b'\x00' * (COMMAND_LENGTH - len(cmd_bytes)))
    
    payload_len = len(payload)
    checksum = hash256(payload)[:4]
    
    header = (
        MAGIC_BYTES +
        cmd_padded +
        struct.pack('<I', payload_len) +
        checksum
    )
    return header + payload


def parse_header(header_bytes: bytes) -> Tuple[bytes, str, int, bytes]:
    """Parse 24-byte header. Returns (magic, command, payload_len, checksum)."""
    if len(header_bytes) != HEADER_LENGTH:
        raise ValueError("Header must be exactly 24 bytes")
        
    magic = header_bytes[:4]
    cmd_raw = header_bytes[4:16]
    command = cmd_raw.rstrip(b'\x00').decode('ascii', errors='ignore')
    payload_len = struct.unpack('<I', header_bytes[16:20])[0]
    checksum = header_bytes[20:24]
    
    return magic, command, payload_len, checksum


# ==============================================================================
# Message Payload Builders and Parsers
# ==============================================================================

def build_version_payload(best_height: int, local_nonce: int = 12345678, user_agent: str = "/QuantyCoin:4.0.0/") -> bytes:
    """Build 'version' handshake payload."""
    res = bytearray()
    res += struct.pack('<i', 70040) # Protocol version 70040 (QTY4)
    res += struct.pack('<Q', 1)     # Services (NODE_NETWORK = 1)
    res += struct.pack('<q', int(time.time()))
    res += b'\x00' * 26            # addr_recv
    res += b'\x00' * 26            # addr_from
    res += struct.pack('<Q', local_nonce)
    ua_bytes = user_agent.encode('utf-8')
    res += bytes([len(ua_bytes)]) + ua_bytes
    res += struct.pack('<i', best_height)
    res += b'\x01'                 # Relay flag
    return bytes(res)


def parse_version_payload(payload: bytes) -> Dict[str, Any]:
    """Parse 'version' payload."""
    version = struct.unpack('<i', payload[:4])[0]
    services = struct.unpack('<Q', payload[4:12])[0]
    timestamp = struct.unpack('<q', payload[12:20])[0]
    nonce = struct.unpack('<Q', payload[72:80])[0]
    ua_len = payload[80]
    user_agent = payload[81:81+ua_len].decode('utf-8', errors='ignore')
    start_height = struct.unpack('<i', payload[81+ua_len:81+ua_len+4])[0]
    return {
        "version": version,
        "services": services,
        "timestamp": timestamp,
        "nonce": nonce,
        "user_agent": user_agent,
        "start_height": start_height
    }


def build_inv_payload(items: List[Tuple[int, bytes]]) -> bytes:
    """Build 'inv' or 'getdata' payload for list of (type, 32-byte hash)."""
    res = bytearray()
    res += bytes([len(items)])
    for inv_type, inv_hash in items:
        res += struct.pack('<I', inv_type)
        res += inv_hash
    return bytes(res)


def parse_inv_payload(payload: bytes) -> List[Tuple[int, bytes]]:
    count = payload[0]
    offset = 1
    items = []
    for _ in range(count):
        inv_type = struct.unpack('<I', payload[offset:offset+4])[0]
        inv_hash = payload[offset+4:offset+36]
        offset += 36
        items.append((inv_type, inv_hash))
    return items


def build_ping_payload(nonce: int) -> bytes:
    return struct.pack('<Q', nonce)


def parse_ping_payload(payload: bytes) -> int:
    return struct.unpack('<Q', payload[:8])[0]
