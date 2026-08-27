"""
QuantyCoin Wallet Command-Line Interface (quanty-wallet)
"""

import sys
import os
import argparse
from .hd_wallet import HDWallet, generate_qr_ascii
from .rpc_client import WalletRPCClient


def run_wallet_cli():
    parser = argparse.ArgumentParser(description="QuantyCoin Standalone Light Wallet (quanty-wallet)")
    subparsers = parser.add_subparsers(dest="command", help="Wallet commands")
    
    # create
    subparsers.add_parser("create", help="Create a new BIP39 HD wallet")
    
    # restore
    p_restore = subparsers.add_parser("restore", help="Restore wallet from BIP39 mnemonic")
    p_restore.add_argument("--mnemonic", type=str, required=True, help="24-word or 12-word recovery phrase")
    
    # balance
    p_bal = subparsers.add_parser("balance", help="Check wallet balance via RPC")
    p_bal.add_argument("--address", type=str, required=True, help="QuantyCoin address (qty1q...)")
    p_bal.add_argument("--rpc", type=str, default="127.0.0.1:19889", help="Node RPC host:port")
    
    # send
    p_send = subparsers.add_parser("send", help="Send QTY to an address")
    p_send.add_argument("--mnemonic", type=str, required=True, help="Sender BIP39 mnemonic phrase")
    p_send.add_argument("--to", type=str, required=True, help="Recipient QuantyCoin address")
    p_send.add_argument("--amount", type=float, required=True, help="Amount in QTY")
    p_send.add_argument("--fee", type=float, default=0.0001, help="Transaction fee in QTY (default 0.0001)")
    p_send.add_argument("--rpc", type=str, default="127.0.0.1:19889", help="Node RPC host:port")
    
    # receive (QR code)
    p_recv = subparsers.add_parser("receive", help="Display address and ASCII QR code")
    p_recv.add_argument("--address", type=str, required=True, help="Receiving address")
    
    args = parser.parse_args()
    
    if args.command == "create":
        wallet = HDWallet()
        print("\n========================================================")
        print("QUANTYCOIN BIP39 HD WALLET CREATED")
        print("========================================================")
        print(f"24-Word Recovery Phrase:\n{wallet.mnemonic}\n")
        print(f"Primary Address (qty1q...): {wallet.get_receiving_address(0)}")
        print("========================================================")
        print("[!] Back up your 24 words securely. Never share them with anyone.\n")
        
    elif args.command == "restore":
        wallet = HDWallet(mnemonic=args.mnemonic)
        print(f"\nWallet Restored Successfully!")
        print(f"Primary Address: {wallet.get_receiving_address(0)}")
        
    elif args.command == "balance":
        host, port = args.rpc.split(":")
        client = WalletRPCClient(rpc_host=host, rpc_port=int(port))
        try:
            res = client.get_address_balance(args.address)
            print(f"\nAddress: {args.address}")
            print(f"Balance: {res['balance']} QTY ({res['balance_sat']:,} Satoshis)")
            print(f"UTXO Count: {res['utxo_count']}")
        except Exception as e:
            print(f"RPC Query Error: {e}")
            
    elif args.command == "send":
        host, port = args.rpc.split(":")
        client = WalletRPCClient(rpc_host=host, rpc_port=int(port))
        wallet = HDWallet(mnemonic=args.mnemonic)
        sender_addr = wallet.get_receiving_address(0)
        
        try:
            utxos = client.get_address_utxos(sender_addr)
            amt_sat = int(args.amount * 100_000_000)
            fee_sat = int(args.fee * 100_000_000)
            
            tx = wallet.build_transaction(
                destination_address=args.to,
                amount_sat=amt_sat,
                available_utxos=utxos,
                fee_sat=fee_sat
            )
            raw_hex = tx.serialize(include_witness=True).hex()
            txid = client.send_raw_transaction(raw_hex)
            print(f"\n[TX BROADCAST SUCCESS] TXID: {txid}")
        except Exception as e:
            print(f"Transaction Error: {e}")
            
    elif args.command == "receive":
        print(f"\nReceiving Address: {args.address}")
        print(generate_qr_ascii(args.address))
    else:
        parser.print_help()


if __name__ == "__main__":
    run_wallet_cli()
