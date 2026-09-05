#!/usr/bin/env bash
# Build Universal Linux AppImage for QuantyCoin QTY2
set -euo pipefail

APP_NAME="QuantyCoin"
VERSION="2.0.0"
APPDIR="dist/AppDir"

echo "Assembling AppDir for QTY2..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/icons"

if [ -f "dist/bin/suite/QuantyCoinSuite" ]; then
  cp "dist/bin/suite/QuantyCoinSuite" "${APPDIR}/usr/bin/quanty-suite"
  chmod +x "${APPDIR}/usr/bin/quanty-suite"
elif [ -f "dist/bin/quanty-suite" ]; then
  cp "dist/bin/quanty-suite" "${APPDIR}/usr/bin/quanty-suite"
  chmod +x "${APPDIR}/usr/bin/quanty-suite"
fi

if [ -f "share/pixmaps/quantycoin.png" ]; then
  cp "share/pixmaps/quantycoin.png" "${APPDIR}/usr/share/icons/quantycoin.png"
fi

cat << EOF > "${APPDIR}/AppRun"
#!/bin/sh
HERE="\$(dirname "\$(readlink -f "\${0}")")"
exec "\${HERE}/usr/bin/quanty-suite" "\$@"
EOF
chmod +x "${APPDIR}/AppRun"

cat << EOF > "${APPDIR}/quantycoin.desktop"
[Desktop Entry]
Name=QuantyCoin Suite
Exec=quanty-suite
Icon=quantycoin
Type=Application
Categories=Network;Finance;
EOF

echo "AppImage recipe ready."
