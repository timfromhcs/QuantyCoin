"""
QuantyCoin Core - Block Header & Full Block Data Model
Binary Serialization, Proof-of-Work Verification & Merkle Validation
"""

import struct
from typing import List, Tuple, Dict, Any, Optional
from crypto import hash256, compute_merkle_root
from .transaction import Transaction, _encode_varint, _decode_varint


class BlockHeader:
    """QuantyCoin 80-byte Block Header."""
    def __init__(self, version: int, prev_block: bytes, merkle_root: bytes, timestamp: int, bits: int, nonce: int):
        self.version = version          # 4 bytes int32 (LE)
        self.prev_block = prev_block    # 32 bytes (LE)
        self.merkle_root = merkle_root  # 32 bytes (LE)
        self.timestamp = timestamp      # 4 bytes uint32 (LE)
        self.bits = bits                # 4 bytes uint32 (LE)
        self.nonce = nonce              # 4 bytes uint32 (LE)

    def serialize(self) -> bytes:
        return (
            struct.pack('<i', self.version) +
            self.prev_block +
            self.merkle_root +
            struct.pack('<I', self.timestamp) +
            struct.pack('<I', self.bits) +
            struct.pack('<I', self.nonce)
        )

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple['BlockHeader', int]:
        if len(data) < 80:
            raise ValueError("Data too short for BlockHeader")
        version = struct.unpack('<i', data[0:4])[0]
        prev_block = data[4:36]
        merkle_root = data[36:68]
        timestamp = struct.unpack('<I', data[68:72])[0]
        bits = struct.unpack('<I', data[72:76])[0]
        nonce = struct.unpack('<I', data[76:80])[0]
        return cls(version, prev_block, merkle_root, timestamp, bits, nonce), 80

    @property
    def hash(self) -> bytes:
        return hash256(self.serialize())

    @property
    def hash_hex(self) -> str:
        return self.hash[::-1].hex()

    def get_target(self) -> int:
        exponent = self.bits >> 24
        coefficient = self.bits & 0x00FFFFFF
        if exponent <= 3:
            return coefficient >> (8 * (3 - exponent))
        else:
            return coefficient << (8 * (exponent - 3))

    def verify_pow(self) -> bool:
        target = self.get_target()
        hash_int = int.from_bytes(self.hash[::-1], 'big')
        return hash_int <= target

    def mine(self) -> int:
        """Find a nonce that satisfies the PoW target."""
        while not self.verify_pow():
            self.nonce = (self.nonce + 1) & 0xFFFFFFFF
        return self.nonce

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash_hex,
            "version": self.version,
            "previousblockhash": self.prev_block[::-1].hex(),
            "merkleroot": self.merkle_root[::-1].hex(),
            "time": self.timestamp,
            "bits": f"{self.bits:08x}",
            "nonce": self.nonce
        }


class Block:
    """Full QuantyCoin Block consisting of Header and Transactions."""
    def __init__(self, header: BlockHeader, transactions: Optional[List[Transaction]] = None):
        self.header = header
        self.transactions = transactions or []

    @property
    def hash(self) -> bytes:
        return self.header.hash

    @property
    def hash_hex(self) -> str:
        return self.header.hash_hex

    def calculate_merkle_root(self) -> bytes:
        tx_hashes = [tx.txid for tx in self.transactions]
        return compute_merkle_root(tx_hashes)

    def verify_merkle_root(self) -> bool:
        return self.calculate_merkle_root() == self.header.merkle_root

    def serialize(self) -> bytes:
        res = bytearray()
        res += self.header.serialize()
        res += _encode_varint(len(self.transactions))
        for tx in self.transactions:
            res += tx.serialize(include_witness=True)
        return bytes(res)

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple['Block', int]:
        header, offset = BlockHeader.deserialize(data)
        tx_count, vlen = _decode_varint(data[offset:])
        offset += vlen
        
        transactions = []
        for _ in range(tx_count):
            tx, tx_len = Transaction.deserialize(data[offset:])
            offset += tx_len
            transactions.append(tx)
            
        return cls(header=header, transactions=transactions), offset

    def validate_structure(self) -> Tuple[bool, str]:
        """Perform stateless structural validations on the block."""
        if not self.header.verify_pow():
            return False, "Invalid Proof-of-Work"
            
        if not self.transactions:
            return False, "Block has no transactions"
            
        if not self.transactions[0].is_coinbase():
            return False, "First transaction is not coinbase"
            
        for i, tx in enumerate(self.transactions[1:], start=1):
            if tx.is_coinbase():
                return False, f"Transaction {i} is an illegal additional coinbase"
                
        if not self.verify_merkle_root():
            return False, "Merkle root mismatch"
            
        raw_size = len(self.serialize())
        if raw_size > 32 * 1024 * 1024: # 32 MB limit
            return False, "Block size exceeds 32 MB limit"
            
        return True, "Valid"

    def to_dict(self) -> Dict[str, Any]:
        d = self.header.to_dict()
        d.update({
            "size": len(self.serialize()),
            "tx_count": len(self.transactions),
            "tx": [tx.txid_hex for tx in self.transactions],
            "raw_tx": [tx.to_dict() for tx in self.transactions],
            "hex": self.serialize().hex()
        })
        return d
