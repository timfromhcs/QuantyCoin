"""
QuantyCoin Core - Transaction Model & Binary Serialization
Zero-Mock Production Implementation (BIP141 SegWit & Standard QuantyCoin Serialization)
"""

import struct
import copy
from typing import List, Optional, Tuple, Dict, Any
from crypto import hash256, hash160, ecdsa_sign, ecdsa_verify, privkey_to_pubkey, encode_der_signature, decode_der_signature
from crypto.bip32_44 import encode_segwit_address, MAINNET_BECH32_HRP


class TxIn:
    """Transaction Input (references a previous UTXO)."""
    def __init__(self, prev_txid: bytes, prev_vout: int, script_sig: bytes = b'', sequence: int = 0xFFFFFFFF, witness: Optional[List[bytes]] = None):
        self.prev_txid = prev_txid  # 32 bytes
        self.prev_vout = prev_vout  # 4 bytes unsigned int
        self.script_sig = script_sig  # variable bytes
        self.sequence = sequence    # 4 bytes unsigned int
        self.witness = witness or [] # List of witness items (bytes)

    def is_coinbase(self) -> bool:
        return self.prev_txid == (b'\x00' * 32) and self.prev_vout == 0xFFFFFFFF

    def serialize(self) -> bytes:
        res = bytearray()
        res += self.prev_txid
        res += struct.pack('<I', self.prev_vout)
        res += _encode_varint(len(self.script_sig))
        res += self.script_sig
        res += struct.pack('<I', self.sequence)
        return bytes(res)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.prev_txid[::-1].hex(),
            "vout": self.prev_vout,
            "scriptSig": {"hex": self.script_sig.hex()},
            "sequence": self.sequence,
            "witness": [w.hex() for w in self.witness]
        }


class TxOut:
    """Transaction Output (specifies value and locking script)."""
    def __init__(self, value: int, script_pubkey: bytes):
        self.value = value  # Satoshis (1 QTY = 100,000,000 Satoshis)
        self.script_pubkey = script_pubkey  # Locking script bytes

    def serialize(self) -> bytes:
        res = bytearray()
        res += struct.pack('<Q', self.value)
        res += _encode_varint(len(self.script_pubkey))
        res += self.script_pubkey
        return bytes(res)

    def get_address(self) -> str:
        """Derive standard destination address from scriptPubKey."""
        # P2WPKH: 0x00 0x14 [20-byte hash]
        if len(self.script_pubkey) == 22 and self.script_pubkey[:2] == b'\x00\x14':
            witness_prog = self.script_pubkey[2:]
            return encode_segwit_address(MAINNET_BECH32_HRP, 0, witness_prog)
        # P2PKH: OP_DUP OP_HASH160 0x14 [20-byte hash] OP_EQUALVERIFY OP_CHECKSIG
        elif len(self.script_pubkey) == 25 and self.script_pubkey[:3] == b'\x76\xa9\x14' and self.script_pubkey[-2:] == b'\x88\xac':
            pub_hash = self.script_pubkey[3:23]
            from crypto.bip32_44 import base58check_encode, MAINNET_PUBKEY_HASH_PREFIX
            return base58check_encode(pub_hash, MAINNET_PUBKEY_HASH_PREFIX)
        return f"script:{self.script_pubkey.hex()}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value / 100_000_000,
            "value_sat": self.value,
            "scriptPubKey": {
                "hex": self.script_pubkey.hex(),
                "address": self.get_address()
            }
        }


class Transaction:
    """QuantyCoin Transaction with full SegWit witness serialization & verification."""
    def __init__(self, version: int = 1, vin: Optional[List[TxIn]] = None, vout: Optional[List[TxOut]] = None, locktime: int = 0):
        self.version = version
        self.vin = vin or []
        self.vout = vout or []
        self.locktime = locktime

    @property
    def has_witness(self) -> bool:
        return any(bool(inp.witness) for inp in self.vin)

    def is_coinbase(self) -> bool:
        return len(self.vin) == 1 and self.vin[0].is_coinbase()

    def serialize(self, include_witness: bool = True) -> bytes:
        res = bytearray()
        res += struct.pack('<i', self.version)
        
        use_witness = include_witness and self.has_witness
        if use_witness:
            res += b'\x00\x01'  # Marker and Flag for SegWit
            
        res += _encode_varint(len(self.vin))
        for inp in self.vin:
            res += inp.serialize()
            
        res += _encode_varint(len(self.vout))
        for out in self.vout:
            res += out.serialize()
            
        if use_witness:
            for inp in self.vin:
                res += _encode_varint(len(inp.witness))
                for w in inp.witness:
                    res += _encode_varint(len(w))
                    res += w
                    
        res += struct.pack('<I', self.locktime)
        return bytes(res)

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple['Transaction', int]:
        offset = 0
        version = struct.unpack('<i', data[offset:offset+4])[0]
        offset += 4
        
        has_witness = False
        if data[offset:offset+2] == b'\x00\x01':
            has_witness = True
            offset += 2
            
        vin_count, varint_len = _decode_varint(data[offset:])
        offset += varint_len
        
        vin = []
        for _ in range(vin_count):
            prev_txid = data[offset:offset+32]
            offset += 32
            prev_vout = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            script_len, vlen = _decode_varint(data[offset:])
            offset += vlen
            script_sig = data[offset:offset+script_len]
            offset += script_len
            sequence = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            vin.append(TxIn(prev_txid, prev_vout, script_sig, sequence))
            
        vout_count, varint_len = _decode_varint(data[offset:])
        offset += varint_len
        
        vout = []
        for _ in range(vout_count):
            value = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            script_len, vlen = _decode_varint(data[offset:])
            offset += vlen
            script_pubkey = data[offset:offset+script_len]
            offset += script_len
            vout.append(TxOut(value, script_pubkey))
            
        if has_witness:
            for inp in vin:
                wit_count, vlen = _decode_varint(data[offset:])
                offset += vlen
                witness = []
                for _ in range(wit_count):
                    item_len, ilen = _decode_varint(data[offset:])
                    offset += ilen
                    item = data[offset:offset+item_len]
                    offset += item_len
                    witness.append(item)
                inp.witness = witness
                
        locktime = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        tx = cls(version=version, vin=vin, vout=vout, locktime=locktime)
        return tx, offset

    @property
    def txid(self) -> bytes:
        """Standard legacy transaction hash (excludes witness)."""
        return hash256(self.serialize(include_witness=False))

    @property
    def txid_hex(self) -> str:
        """Hex representation in RPC little-endian order."""
        return self.txid[::-1].hex()

    @property
    def wtxid(self) -> bytes:
        """Witness transaction hash."""
        return hash256(self.serialize(include_witness=True))

    @property
    def wtxid_hex(self) -> str:
        return self.wtxid[::-1].hex()

    def get_sighash(self, input_index: int, prev_script: bytes, prev_amount: int = 0) -> bytes:
        """
        BIP143 / Standard Signature Hash computation for input index.
        """
        # BIP143 SegWit Sighash
        hash_prevouts = hash256(b''.join(inp.prev_txid + struct.pack('<I', inp.prev_vout) for inp in self.vin))
        hash_sequence = hash256(b''.join(struct.pack('<I', inp.sequence) for inp in self.vin))
        hash_outputs = hash256(b''.join(out.serialize() for out in self.vout))
        
        inp = self.vin[input_index]
        outpoint = inp.prev_txid + struct.pack('<I', inp.prev_vout)
        
        # P2WPKH scriptCode: 0x19 0x76 0xa9 0x14 [20-byte hash] 0x88 0xac
        if prev_script.startswith(b'\x00\x14'):
            script_code = b'\x19\x76\xa9\x14' + prev_script[2:] + b'\x88\xac'
        else:
            script_code = bytes([len(prev_script)]) + prev_script
            
        preimage = bytearray()
        preimage += struct.pack('<i', self.version)
        preimage += hash_prevouts
        preimage += hash_sequence
        preimage += outpoint
        preimage += script_code
        preimage += struct.pack('<Q', prev_amount)
        preimage += struct.pack('<I', inp.sequence)
        preimage += hash_outputs
        preimage += struct.pack('<I', self.locktime)
        preimage += struct.pack('<I', 1) # SIGHASH_ALL (0x01)
        
        return hash256(bytes(preimage))

    def sign_input(self, input_index: int, privkey_bytes: bytes, prev_script: bytes, prev_amount: int) -> None:
        """Sign input_index with private key and attach witness signature."""
        sighash = self.get_sighash(input_index, prev_script, prev_amount)
        r, s = ecdsa_sign(sighash, privkey_bytes)
        der_sig = encode_der_signature(r, s) + b'\x01' # Append SIGHASH_ALL byte
        pubkey = privkey_to_pubkey(privkey_bytes, compressed=True)
        self.vin[input_index].witness = [der_sig, pubkey]

    def verify_input_signature(self, input_index: int, prev_script: bytes, prev_amount: int) -> bool:
        """Verify witness signature on input_index."""
        if input_index >= len(self.vin):
            return False
        inp = self.vin[input_index]
        if len(inp.witness) != 2:
            return False
        der_sig_with_type, pubkey = inp.witness[0], inp.witness[1]
        if len(der_sig_with_type) < 2:
            return False
        der_sig = der_sig_with_type[:-1]
        sighash_type = der_sig_with_type[-1]
        if sighash_type != 1: # SIGHASH_ALL
            return False
            
        # Verify pubkey matches prev_script
        pub_hash = hash160(pubkey)
        if prev_script == (b'\x00\x14' + pub_hash) or prev_script == (b'\x76\xa9\x14' + pub_hash + b'\x88\xac'):
            pass
        else:
            return False
            
        try:
            r, s = decode_der_signature(der_sig)
            sighash = self.get_sighash(input_index, prev_script, prev_amount)
            return ecdsa_verify(sighash, pubkey, r, s)
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.txid_hex,
            "hash": self.wtxid_hex,
            "version": self.version,
            "size": len(self.serialize(include_witness=True)),
            "vsize": (len(self.serialize(include_witness=False)) * 3 + len(self.serialize(include_witness=True)) + 3) // 4,
            "locktime": self.locktime,
            "vin": [inp.to_dict() for inp in self.vin],
            "vout": [out.to_dict() for out in self.vout],
            "hex": self.serialize(include_witness=True).hex()
        }


def _encode_varint(val: int) -> bytes:
    if val < 0xFD:
        return bytes([val])
    elif val <= 0xFFFF:
        return b'\xFD' + struct.pack('<H', val)
    elif val <= 0xFFFFFFFF:
        return b'\xFE' + struct.pack('<I', val)
    else:
        return b'\xFF' + struct.pack('<Q', val)


def _decode_varint(data: bytes) -> Tuple[int, int]:
    if not data:
        raise ValueError("Buffer empty for varint")
    first = data[0]
    if first < 0xFD:
        return first, 1
    elif first == 0xFD:
        return struct.unpack('<H', data[1:3])[0], 3
    elif first == 0xFE:
        return struct.unpack('<I', data[1:5])[0], 5
    else:
        return struct.unpack('<Q', data[1:9])[0], 9
