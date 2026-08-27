"""
QuantyCoin Miner Command-Line Interface (quanty-miner)
"""

import sys
import time
import argparse
from .engine import MiningEngine
from .stratum import StratumServer


def run_miner_cli():
    parser = argparse.ArgumentParser(description="QuantyCoin Multi-Threaded Miner (quanty-miner)")
    parser.add_argument("--address", type=str, required=True, help="Coinbase payout address (qty1q...)")
    parser.add_argument("--threads", type=int, default=4, help="Number of CPU mining worker threads")
    parser.add_argument("--rpc", type=str, default="127.0.0.1:19889", help="Node RPC host:port")
    parser.add_argument("--stratum-server", action="store_true", help="Also start local Stratum server on port 3333")
    args = parser.parse_args()
    
    host, port = args.rpc.split(":")
    engine = MiningEngine(payout_address=args.address, rpc_host=host, rpc_port=int(port), threads=args.threads)
    
    stratum = None
    if args.stratum_server:
        stratum = StratumServer()
        stratum.start()
        
    print("================================================================")
    print("QUANTYCOIN MULTI-THREADED MINER v3.0")
    print(f"Payout Address:  {args.address}")
    print(f"Worker Threads:  {args.threads}")
    print(f"Connected Node:  http://{args.rpc}")
    print("================================================================")
    
    engine.start()
    
    try:
        while True:
            time.sleep(2)
            t = engine.get_telemetry()
            print(f"\r[MINING] Hashrate: {t['hashrate_khs']} kH/s | Total Hashes: {t['total_hashes']:,} | Blocks Found: {t['blocks_mined']}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nStopping miner...")
        engine.stop()
        if stratum:
            stratum.stop()


if __name__ == "__main__":
    run_miner_cli()
