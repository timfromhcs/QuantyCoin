#!/usr/bin/env bash
# Build Debian/Ubuntu .deb package for QuantyCoin v6.0
set -euo pipefail

PACKAGE_NAME="quantycoin"
VERSION="6.0.0"
ARCH="amd64"
DEB_DIR="dist/deb/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "Creating Debian package structure..."
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/local/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps"

cat << EOF > "${DEB_DIR}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: QuantyCoin Core Contributors <timfromhcs@gmail.com>
Description: QuantyCoin Layer-1 Quantum & AI Era Modular Blockchain Suite
 Native Qt6 full node daemon, BIP39 HD wallet, and multi-threaded miner.
EOF

# Copy binaries
cp dist/bin/quantyd "${DEB_DIR}/usr/local/bin/" 2>/dev/null || true
cp dist/bin/quanty-wallet "${DEB_DIR}/usr/local/bin/" 2>/dev/null || true
cp dist/bin/quanty-miner "${DEB_DIR}/usr/local/bin/" 2>/dev/null || true
cp dist/bin/quanty-suite "${DEB_DIR}/usr/local/bin/" 2>/dev/null || true

dpkg-deb --build "${DEB_DIR}" "dist/linux/QuantyCoin-${VERSION}-${ARCH}.deb"
echo "Debian package created: dist/linux/QuantyCoin-${VERSION}-${ARCH}.deb"
