#!/usr/bin/env bash
# Build Universal macOS DMG package for QuantyCoin QTY2
set -euo pipefail

APP_NAME="QuantyCoinSuite"
VERSION="2.0.0"
DMG_NAME="QuantyCoin-${VERSION}-macOS-Universal.dmg"

echo "Building macOS .app bundle for QuantyCoin QTY2..."
mkdir -p "dist/macos/${APP_NAME}.app/Contents/MacOS"
mkdir -p "dist/macos/${APP_NAME}.app/Contents/Resources"

cat << EOF > "dist/macos/${APP_NAME}.app/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>QuantyCoinSuite</string>
    <key>CFBundleIconFile</key>
    <string>quantycoin.icns</string>
    <key>CFBundleIdentifier</key>
    <string>org.quantycoin.suite</string>
    <key>CFBundleName</key>
    <string>QuantyCoin</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
</dict>
</plist>
EOF

if [ -f "dist/bin/suite/QuantyCoinSuite" ]; then
  cp "dist/bin/suite/QuantyCoinSuite" "dist/macos/${APP_NAME}.app/Contents/MacOS/"
  chmod +x "dist/macos/${APP_NAME}.app/Contents/MacOS/QuantyCoinSuite"
elif [ -f "dist/bin/quanty-suite" ]; then
  cp "dist/bin/quanty-suite" "dist/macos/${APP_NAME}.app/Contents/MacOS/QuantyCoinSuite"
  chmod +x "dist/macos/${APP_NAME}.app/Contents/MacOS/QuantyCoinSuite"
fi

echo "Creating DMG Image..."
if command -v hdiutil >/dev/null 2>&1; then
  hdiutil create -volname "${APP_NAME}" -srcfolder "dist/macos/${APP_NAME}.app" -ov -format UDZO "dist/macos/${DMG_NAME}"
  echo "DMG created: dist/macos/${DMG_NAME}"
else
  echo "hdiutil not available; packaging will proceed via tarball."
fi
