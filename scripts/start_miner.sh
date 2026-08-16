#!/usr/bin/env bash
set -e

ADDRESS="${1:-qty1qa8639f6b36aa83d174f6ff8f608084a9475678b1}"
BLOCKS="${2:-1}"

echo "========================================================="
echo "           QuantyCoin (QTY) Automated Miner             "
echo "========================================================="
echo "Target Mining Address: $ADDRESS"
echo "Blocks per iteration: $BLOCKS"

while true; do
    echo "[$(date)] Mining $BLOCKS block(s)..."
    ./src/qty-cli generatetoaddress "$BLOCKS" "$ADDRESS" || true
    sleep 60
done
