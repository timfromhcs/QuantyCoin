"""
QuantyCoin Miner Command-Line Interface (quanty-miner)
"""

import sys
import time
import argparse
from .engine import MiningEngine
from .stratum import StratumServer


def run_miner_cli():
    parser = argparse.ArgumentParser(description="QuantyCoin Multi-Threaded Dual-PoW Miner (quanty-miner)")
    parser.add_argument("--address", type=str, required=True, help="Coinbase payout address (qty1q..., qty1p..., qty1z...)")
    parser.add_argument("--threads", type=int, default=4, help="Number of CPU mining worker threads")
    parser.add_argument("--rpc", type=str, default="127.0.0.1:19889", help="Node RPC host:port")
    parser.add_argument("--lane", type=str, choices=["sha256d", "general", "0", "1"], default="general", help="PoW Mining Lane: sha256d (ASIC Lane A) or general (CPU/GPU Lane B)")
    parser.add_argument("--stratum-server", action="store_true", help="Also start local Stratum V1 server on port 3333")
    parser.add_argument("--stratum-v2", action="store_true", help="Also start local Stratum V2 server on port 3334")
    args = parser.parse_args()
    
    pow_type = 1 if args.lane in ("general", "1") else 0
    lane_label = "LANE_B (General-Purpose CPU/GPU Scrypt)" if pow_type == 1 else "LANE_A (SHA-256D ASIC)"
    
    host, port = args.rpc.split(":")
    engine = MiningEngine(payout_address=args.address, rpc_host=host, rpc_port=int(port), threads=args.threads, pow_type=pow_type)
    
    stratum = None
    if args.stratum_server:
        stratum = StratumServer()
        stratum.start()

    sv2 = None
    if args.stratum_v2:
        from .stratum_v2 import StratumV2Server
        sv2 = StratumV2Server()
        sv2.start()
        
    print("================================================================")
    print("QUANTYCOIN MULTI-THREADED DUAL-POW MINER v3.0")
    print(f"Mining Lane:     {lane_label}")
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
        if sv2:
            sv2.stop()


if __name__ == "__main__":
    run_miner_cli()
