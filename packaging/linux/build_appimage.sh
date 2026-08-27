#!/usr/bin/env bash
# Build Standalone Linux AppImage for QuantyCoin v6.0
set -euo pipefail

APP_NAME="QuantyCoin"
VERSION="6.0.0"
APPDIR="dist/AppDir"

echo "Assembling AppDir for v6.0..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/icons"

cp dist/bin/quanty-suite "${APPDIR}/usr/bin/quanty-suite" 2>/dev/null || true
cp share/pixmaps/quantycoin.png "${APPDIR}/usr/share/icons/quantycoin.png" 2>/dev/null || true

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

echo "AppImage recipe ready. Packaging with appimagetool..."
