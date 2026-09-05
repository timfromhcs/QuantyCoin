#!/usr/bin/env bash
# Build Debian/Ubuntu .deb package for QuantyCoin QTY2
set -euo pipefail

PACKAGE_NAME="quantycoin"
VERSION="2.0.0"
ARCH="amd64"
DEB_DIR="dist/deb/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "Creating Debian package structure..."
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/local/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "dist/linux"

cat << EOF > "${DEB_DIR}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: QuantyCoin Core Contributors <timfromhcs@gmail.com>
Description: QuantyCoin Layer-1 SHA-256D Proof-of-Work Blockchain Protocol
 Native Qt6 full node daemon, BIP39 HD wallet, and multi-threaded miner.
EOF

for bin in quantyd quanty-wallet quanty-miner; do
  if [ -f "dist/bin/${bin}" ]; then
    cp "dist/bin/${bin}" "${DEB_DIR}/usr/local/bin/"
    chmod +x "${DEB_DIR}/usr/local/bin/${bin}"
  fi
done
if [ -f "dist/bin/suite/QuantyCoinSuite" ]; then
  cp "dist/bin/suite/QuantyCoinSuite" "${DEB_DIR}/usr/local/bin/quanty-suite"
  chmod +x "${DEB_DIR}/usr/local/bin/quanty-suite"
fi

if command -v dpkg-deb >/dev/null 2>&1; then
  dpkg-deb --build "${DEB_DIR}" "dist/linux/QuantyCoin-${VERSION}-${ARCH}.deb"
  echo "Debian package created: dist/linux/QuantyCoin-${VERSION}-${ARCH}.deb"
else
  echo "dpkg-deb not found; skipping .deb creation."
fi
