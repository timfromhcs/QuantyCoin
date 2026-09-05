"""
QuantyCoin HD Wallet Engine
BIP39 / BIP44 Multi-Account Hierarchical Deterministic Wallet
Coin Selection, Transaction Signing & QR Code Generation
"""

import os
import json
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from crypto import (
    generate_mnemonic, validate_mnemonic, mnemonic_to_seed,
    HDKey, hash160, sha256
)
from crypto.bip32_44 import encode_segwit_address, MAINNET_BECH32_HRP
from crypto.mldsa import MLDSAKey
from core.transaction import Transaction, TxIn, TxOut, SignatureType


class HDWallet:
    """Production Multi-Account BIP44 HD Wallet for QuantyCoin with Post-Quantum Capability."""
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
        self.pq_keys: Dict[int, MLDSAKey] = {}
        self.pq_addresses: Dict[int, str] = {}
        self.hybrid_addresses: Dict[int, str] = {}
        
        # Pre-derive first 5 receiving addresses
        for i in range(5):
            self.get_receiving_address(i)
            self.get_pq_address(i)
            self.get_hybrid_address(i)

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

    def get_pq_key(self, index: int = 0) -> MLDSAKey:
        """Deterministically derive ML-DSA keypair from HD seed and derivation path."""
        if index not in self.pq_keys:
            # Deterministic domain-separated seed derivation for ML-DSA
            path_str = f"m/44'/999'/{self.account_index}'/pq/{index}"
            pq_seed = hashlib.sha256(self.seed + path_str.encode('utf-8')).digest()
            self.pq_keys[index] = MLDSAKey.from_seed(pq_seed)
        return self.pq_keys[index]

    def get_pq_address(self, index: int = 0, hrp: str = MAINNET_BECH32_HRP) -> str:
        """Derive Bech32m witness v1 address: qty1p..."""
        if index not in self.pq_addresses:
            k = self.get_pq_key(index)
            prog = sha256(k.public_key)
            self.pq_addresses[index] = encode_segwit_address(hrp, 1, prog)
        return self.pq_addresses[index]

    def get_hybrid_address(self, index: int = 0, hrp: str = MAINNET_BECH32_HRP) -> str:
        """Derive Bech32m witness v2 address: qty1z..."""
        if index not in self.hybrid_addresses:
            secp_key = self.get_receiving_key(index)
            pq_key = self.get_pq_key(index)
            prog = sha256(secp_key.get_public_key() + pq_key.public_key)
            self.hybrid_addresses[index] = encode_segwit_address(hrp, 2, prog)
        return self.hybrid_addresses[index]

    def get_all_known_addresses(self) -> List[str]:
        addrs = []
        for key in self.receiving_keys.values():
            addrs.append(key.get_address())
        for key in self.change_keys.values():
            addrs.append(key.get_address())
        addrs.extend(self.pq_addresses.values())
        addrs.extend(self.hybrid_addresses.values())
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

    def find_pq_key_for_address(self, address: str) -> Optional[Tuple[int, MLDSAKey]]:
        """Find the ML-DSA key matching a qty1p address."""
        for idx, addr in self.pq_addresses.items():
            if addr == address:
                return idx, self.pq_keys[idx]
        for i in range(len(self.pq_addresses), len(self.pq_addresses) + 50):
            addr = self.get_pq_address(i)
            if addr == address:
                return i, self.pq_keys[i]
        return None

    def find_hybrid_keys_for_address(self, address: str) -> Optional[Tuple[int, HDKey, MLDSAKey]]:
        """Find the (HDKey, MLDSAKey) matching a qty1z address."""
        for idx, addr in self.hybrid_addresses.items():
            if addr == address:
                return idx, self.get_receiving_key(idx), self.pq_keys[idx]
        for i in range(len(self.hybrid_addresses), len(self.hybrid_addresses) + 50):
            addr = self.get_hybrid_address(i)
            if addr == address:
                return i, self.get_receiving_key(i), self.pq_keys[i]
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
            
            # Check if input corresponds to a Post-Quantum address (qty1p...)
            pq_match = None
            if addr and addr.startswith("qty1p"):
                pq_match = self.find_pq_key_for_address(addr)
            if not pq_match and len(prev_script) == 34 and prev_script[:2] == b'\x51\x20':
                prog = prev_script[2:]
                for idx, k in self.pq_keys.items():
                    if sha256(k.public_key) == prog:
                        pq_match = (idx, k)
                        break
            if pq_match:
                _, pq_key = pq_match
                tx.sign_input_mldsa(i, pq_key.secret_key, pq_key.public_key, prev_script, prev_amount)
                continue

            # Check if input corresponds to a Hybrid address (qty1z...)
            hybrid_match = None
            if addr and addr.startswith("qty1z"):
                hybrid_match = self.find_hybrid_keys_for_address(addr)
            if not hybrid_match and len(prev_script) == 34 and prev_script[:2] == b'\x52\x20':
                prog = prev_script[2:]
                for idx in range(len(self.receiving_keys)):
                    secp = self.get_receiving_key(idx)
                    pqk = self.get_pq_key(idx)
                    if sha256(secp.get_public_key() + pqk.public_key) == prog:
                        hybrid_match = (idx, secp, pqk)
                        break
            if hybrid_match:
                _, secp_k, pq_k = hybrid_match
                tx.sign_input_hybrid(i, secp_k.key, pq_k.secret_key, pq_k.public_key, prev_script, prev_amount)
                continue

            # Classical ECDSA signing
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

    def get_quantum_vulnerability_report(self, utxos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of UTXOs and categorize them by quantum security status according to MIGRATION_SPEC.
        Identifies vulnerable legacy classical ECDSA outputs vs quantum-resistant outputs.
        """
        vulnerable_utxos = []
        pqc_utxos = []
        hybrid_utxos = []
        vulnerable_total_sat = 0
        pqc_total_sat = 0
        hybrid_total_sat = 0

        for u in utxos:
            addr = u.get("address", "")
            script_hex = u.get("scriptPubKey", "")
            script = bytes.fromhex(script_hex) if script_hex else b""
            val = u.get("value_sat", 0)

            if addr.startswith("qty1p") or (len(script) == 34 and script[:2] == b'\x51\x20'):
                pqc_utxos.append(u)
                pqc_total_sat += val
            elif addr.startswith("qty1z") or (len(script) == 34 and script[:2] == b'\x52\x20'):
                hybrid_utxos.append(u)
                hybrid_total_sat += val
            else:
                # Classical ECDSA (p2wpkh, p2pkh, etc.)
                vulnerable_utxos.append(u)
                vulnerable_total_sat += val

        total_funds = vulnerable_total_sat + pqc_total_sat + hybrid_total_sat
        vulnerability_ratio = (vulnerable_total_sat / total_funds) if total_funds > 0 else 0.0

        return {
            "vulnerable_count": len(vulnerable_utxos),
            "vulnerable_total_sat": vulnerable_total_sat,
            "vulnerable_ratio": vulnerability_ratio,
            "pqc_count": len(pqc_utxos),
            "pqc_total_sat": pqc_total_sat,
            "hybrid_count": len(hybrid_utxos),
            "hybrid_total_sat": hybrid_total_sat,
            "has_vulnerable_utxos": len(vulnerable_utxos) > 0,
            "migration_recommended": len(vulnerable_utxos) > 0,
            "warning_message": (
                f"WARNING: {len(vulnerable_utxos)} UTXOs ({vulnerable_total_sat / 100_000_000:.8f} QTY) rely on "
                "classical Secp256k1 ECDSA and are vulnerable to future Cryptographically Relevant Quantum Computers (CRQCs). "
                "Migrate balances to ML-DSA (qty1p...) or Hybrid (qty1z...) addresses immediately."
                if len(vulnerable_utxos) > 0 else "All UTXOs are protected by Post-Quantum lattice cryptography."
            ),
            "vulnerable_utxos": vulnerable_utxos
        }

    def build_pqc_migration_transaction(self, available_utxos: List[Dict[str, Any]], target_mode: str = "mldsa", fee_sat: int = 10000) -> Transaction:
        """
        Construct and sign an automated migration transaction consolidating all vulnerable classical UTXOs
        into a single quantum-secure address (ML-DSA qty1p... or Hybrid qty1z...).
        """
        report = self.get_quantum_vulnerability_report(available_utxos)
        vulnerable_utxos = report["vulnerable_utxos"]
        if not vulnerable_utxos:
            raise ValueError("No vulnerable classical UTXOs found to migrate.")

        total_val = sum(u["value_sat"] for u in vulnerable_utxos)
        if total_val <= fee_sat:
            raise ValueError(f"Total vulnerable balance ({total_val} sat) is less than or equal to fee ({fee_sat} sat).")

        # Select target post-quantum address
        if target_mode.lower() in ("mldsa", "pq", "pqc"):
            target_address = self.get_pq_address(0)
        elif target_mode.lower() in ("hybrid", "dual"):
            target_address = self.get_hybrid_address(0)
        else:
            raise ValueError(f"Unknown target migration mode: {target_mode}. Expected 'mldsa' or 'hybrid'.")

        migrated_amount = total_val - fee_sat
        return self.build_transaction(
            destination_address=target_address,
            amount_sat=migrated_amount,
            available_utxos=vulnerable_utxos,
            fee_sat=fee_sat
        )

    def create_and_sign_transaction(self, utxos: List[Dict[str, Any]], destination_address: str, amount_sat: int, fee_sat: int = 10000, change_address: Optional[str] = None) -> Tuple[str, str]:
        tx = self.build_transaction(destination_address, amount_sat, utxos, fee_sat, change_address)
        return tx.serialize().hex(), tx.txid_hex


    def export_keystore(self, filepath: str) -> None:
        """Export wallet metadata to file (encrypted/json)."""
        data = {
            "version": 2,
            "account_index": self.account_index,
            "primary_address": self.get_receiving_address(0),
            "receiving_addresses": [k.get_address() for k in self.receiving_keys.values()],
            "change_addresses": [k.get_address() for k in self.change_keys.values()],
            "pq_addresses": list(self.pq_addresses.values()),
            "hybrid_addresses": list(self.hybrid_addresses.values())
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
