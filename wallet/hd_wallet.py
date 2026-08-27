"""
QuantyCoin HD Wallet Engine
BIP39 / BIP44 Multi-Account Hierarchical Deterministic Wallet
Coin Selection, Transaction Signing & QR Code Generation
"""

import os
import json
from typing import List, Dict, Tuple, Optional, Any
from crypto import (
    generate_mnemonic, validate_mnemonic, mnemonic_to_seed,
    HDKey, hash160
)
from core.transaction import Transaction, TxIn, TxOut


class HDWallet:
    """Production Multi-Account BIP44 HD Wallet for QuantyCoin."""
    def __init__(self, mnemonic: Optional[str] = None, passphrase: str = "", account_index: int = 0):
        if mnemonic is None:
            self.mnemonic = generate_mnemonic(256)
        else:
            if not validate_mnemonic(mnemonic):
                raise ValueError("Invalid BIP39 mnemonic")
            self.mnemonic = mnemonic
            
        self.passphrase = passphrase
        self.account_index = account_index
        self.seed = mnemonic_to_seed(self.mnemonic, passphrase)
        self.master_node = HDKey.from_seed(self.seed)
        
        # Base Account Path: m/44'/999'/account'
        self.account_path = f"m/44'/999'/{account_index}'"
        self.account_node = self.master_node.derive_path(self.account_path)
        
        # Internal cache of generated receiving and change keys
        # index -> HDKey
        self.receiving_keys: Dict[int, HDKey] = {}
        self.change_keys: Dict[int, HDKey] = {}
        
        # Pre-derive first 5 receiving addresses
        for i in range(5):
            self.get_receiving_address(i)

    def get_receiving_key(self, index: int = 0) -> HDKey:
        """Derive receiving key at m/44'/999'/account'/0/index."""
        if index not in self.receiving_keys:
            key = self.account_node.derive_child(0).derive_child(index)
            self.receiving_keys[index] = key
        return self.receiving_keys[index]

    def get_change_key(self, index: int = 0) -> HDKey:
        """Derive change key at m/44'/999'/account'/1/index."""
        if index not in self.change_keys:
            key = self.account_node.derive_child(1).derive_child(index)
            self.change_keys[index] = key
        return self.change_keys[index]

    def get_receiving_address(self, index: int = 0) -> str:
        return self.get_receiving_key(index).get_address()

    def get_address(self, index: int = 0) -> str:
        return self.get_receiving_address(index)

    def get_change_address(self, index: int = 0) -> str:
        return self.get_change_key(index).get_address()

    def get_all_known_addresses(self) -> List[str]:
        addrs = []
        for key in self.receiving_keys.values():
            addrs.append(key.get_address())
        for key in self.change_keys.values():
            addrs.append(key.get_address())
        return addrs

    def find_key_for_address(self, address: str) -> Optional[HDKey]:
        """Find the private HDKey matching an address."""
        for key in self.receiving_keys.values():
            if key.get_address() == address:
                return key
        for key in self.change_keys.values():
            if key.get_address() == address:
                return key
        # Search ahead up to 50 addresses
        for i in range(len(self.receiving_keys), len(self.receiving_keys) + 50):
            k = self.get_receiving_key(i)
            if k.get_address() == address:
                return k
        return None

    def build_transaction(self, destination_address: str, amount_sat: int, available_utxos: List[Dict[str, Any]], fee_sat: int = 10000, change_address: Optional[str] = None) -> Transaction:
        """
        Build and sign a complete QuantyCoin transaction using available UTXOs.
        """
        if amount_sat <= 0:
            raise ValueError("Amount must be greater than zero")
            
        required_total = amount_sat + fee_sat
        
        # 1. Coin Selection (Greedy Accumulation)
        selected_utxos: List[Dict[str, Any]] = []
        accumulated_sat = 0
        
        # Sort UTXOs by value descending
        sorted_utxos = sorted(available_utxos, key=lambda u: u["value_sat"], reverse=True)
        
        for utxo in sorted_utxos:
            selected_utxos.append(utxo)
            accumulated_sat += utxo["value_sat"]
            if accumulated_sat >= required_total:
                break
                
        if accumulated_sat < required_total:
            raise ValueError(f"Insufficient funds: Have {accumulated_sat/100_000_000:.8f} QTY, need {required_total/100_000_000:.8f} QTY (including fee)")
            
        # 2. Build Outputs
        from crypto.bip32_44 import address_to_scriptpubkey
        dest_script_pubkey = address_to_scriptpubkey(destination_address)
        outputs = [TxOut(value=amount_sat, script_pubkey=dest_script_pubkey)]
        
        # Change Output
        change_sat = accumulated_sat - required_total
        if change_sat > 1000: # Dust threshold (1000 satoshis)
            if not change_address:
                change_address = self.get_change_address(0)
            change_script_pubkey = address_to_scriptpubkey(change_address)
            outputs.append(TxOut(value=change_sat, script_pubkey=change_script_pubkey))
            
        # 3. Build Inputs
        inputs = []
        for utxo in selected_utxos:
            txid_bytes = bytes.fromhex(utxo["txid"])[::-1]
            vout = utxo["vout"]
            inputs.append(TxIn(prev_txid=txid_bytes, prev_vout=vout))
            
        tx = Transaction(version=1, vin=inputs, vout=outputs, locktime=0)
        
        # 4. Sign Inputs
        for i, utxo in enumerate(selected_utxos):
            addr = utxo.get("address")
            prev_script = bytes.fromhex(utxo["scriptPubKey"])
            prev_amount = utxo["value_sat"]
            
            # Find key
            key = None
            if addr:
                key = self.find_key_for_address(addr)
            if not key:
                # Match by pubkey hash
                for k in list(self.receiving_keys.values()) + list(self.change_keys.values()):
                    if prev_script == (b'\x00\x14' + hash160(k.get_public_key())):
                        key = k
                        break
                        
            if not key:
                # Fallback: check index 0
                key = self.get_receiving_key(0)
                
            tx.sign_input(i, key.key, prev_script, prev_amount)
            
        return tx

    def create_and_sign_transaction(self, utxos: List[Dict[str, Any]], destination_address: str, amount_sat: int, fee_sat: int = 10000, change_address: Optional[str] = None) -> Tuple[str, str]:
        tx = self.build_transaction(destination_address, amount_sat, utxos, fee_sat, change_address)
        return tx.serialize().hex(), tx.txid_hex

    def export_keystore(self, filepath: str) -> None:
        """Export wallet metadata to file (encrypted/json)."""
        data = {
            "version": 1,
            "account_index": self.account_index,
            "primary_address": self.get_receiving_address(0),
            "receiving_addresses": [k.get_address() for k in self.receiving_keys.values()],
            "change_addresses": [k.get_address() for k in self.change_keys.values()]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def generate_qr_ascii(data: str) -> str:
    """Generate ASCII QR code representation for terminal display."""
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=1, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        lines = []
        for row in qr.modules:
            line = "".join("██" if cell else "  " for cell in row)
            lines.append(line)
        return "\n".join(lines)
    except Exception:
        return f"[QR CODE for: {data}]"
