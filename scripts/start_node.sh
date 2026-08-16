#!/usr/bin/env bash
set -e

echo "Starting QuantyCoin Full Node Daemon (qtyd)..."
if [ -f ./src/qtyd ]; then
    ./src/qtyd -daemon -upnp "$@"
    echo "QuantyCoin daemon started successfully."
    echo "Use './src/qty-cli getblockchaininfo' to check node status."
else
    echo "Error: src/qtyd binary not found. Please build QuantyCoin first."
    exit 1
fi
