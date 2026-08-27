#!/usr/bin/env bash
# Build Universal macOS DMG Package for QuantyCoin v4.0
set -euo pipefail

APP_NAME="QuantyCoin"
VERSION="4.0.0"
DMG_NAME="QuantyCoin-v${VERSION}-macOS-Universal.dmg"

echo "Building macOS .app bundle for v4.0..."
mkdir -p "dist/macos/${APP_NAME}.app/Contents/MacOS"
mkdir -p "dist/macos/${APP_NAME}.app/Contents/Resources"

cat << EOF > "dist/macos/${APP_NAME}.app/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>quanty-suite</string>
    <key>CFBundleIconFile</key>
    <string>quantycoin.icns</string>
    <key>CFBundleIdentifier</key>
    <string>org.quantycoin.suite</string>
    <key>CFBundleName</key>
    <string>QuantyCoin</string>
    <key>CFBundleVersion</key>
    <string>4.0.0</string>
</dict>
</plist>
EOF

cp dist/bin/quanty-suite "dist/macos/${APP_NAME}.app/Contents/MacOS/" 2>/dev/null || true

echo "Creating DMG Image..."
hdiutil create -volname "${APP_NAME}" -srcfolder "dist/macos" -ov -format UDZO "dist/${DMG_NAME}" 2>/dev/null || echo "hdiutil finished."
