#!/usr/bin/env bash
set -e

echo "========================================================="
echo "       QuantyCoin (QTY) Automated Build Script          "
echo "========================================================="

# Run autogen if configure is missing
if [ ! -f ./configure ]; then
    echo "[1/3] Running autogen.sh..."
    ./autogen.sh
fi

echo "[2/3] Configuring QuantyCoin build..."
./configure --with-gui=qt5 --enable-upnp-default --disable-bench --disable-fuzz "$@"

echo "[3/3] Compiling binaries with multi-core support..."
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
make -j"$NPROC"

echo "========================================================="
echo " Build Completed Successfully! "
echo " Binaries located in src/:"
echo "   - Full Node Daemon: src/qtyd"
echo "   - RPC CLI Tool:     src/qty-cli"
echo "   - Qt GUI Wallet:    src/qt/qty-qt"
echo "========================================================="
