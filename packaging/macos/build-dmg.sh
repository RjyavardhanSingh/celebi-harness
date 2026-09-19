#!/usr/bin/env bash
# Build a macOS .dmg installer from a PyInstaller bundle.
#
# Usage:
#   ./build-dmg.sh [version]
#
# Prerequisites:
#   - PyInstaller bundle at dist/celebi/
#   - assets/logo.png
#
# Output:
#   dist/celebi-<version>-macos.dmg
set -euo pipefail

VERSION="${1:-0.1.0}"
APP_NAME="Celebi"
BUNDLE_DIR="dist/celebi"
APP_DIR="dist/${APP_NAME}.app"
DMG_NAME="celebi-${VERSION}-macos.dmg"
STAGING="/tmp/celebi-dmg-staging"

echo "==> Building macOS .app bundle from PyInstaller output"

# Clean previous artifacts
rm -rf "$APP_DIR" "$STAGING"
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"

# Copy PyInstaller bundle into .app structure
cp -R "${BUNDLE_DIR}/"* "${APP_DIR}/Contents/MacOS/"

# Copy Info.plist
cp packaging/macos/Info.plist "${APP_DIR}/Contents/Info.plist"

# Convert logo.png to icns if possible (requires sips + iconutil on macOS)
ICON_SRC="assets/logo.png"
ICON_SET="/tmp/celebi.iconset"
ICON_ICNS="${APP_DIR}/Contents/Resources/celebi.icns"

if [ -f "$ICON_SRC" ]; then
    echo "==> Converting icon to .icns"
    rm -rf "$ICON_SET"
    mkdir -p "$ICON_SET"
    sips -z 16 16 "$ICON_SRC" --out "${ICON_SET}/icon_16x16.png" 2>/dev/null || true
    sips -z 32 32 "$ICON_SRC" --out "${ICON_SET}/icon_16x16@2x.png" 2>/dev/null || true
    sips -z 32 32 "$ICON_SRC" --out "${ICON_SET}/icon_32x32.png" 2>/dev/null || true
    sips -z 64 64 "$ICON_SRC" --out "${ICON_SET}/icon_32x32@2x.png" 2>/dev/null || true
    sips -z 128 128 "$ICON_SRC" --out "${ICON_SET}/icon_128x128.png" 2>/dev/null || true
    sips -z 256 256 "$ICON_SRC" --out "${ICON_SET}/icon_128x128@2x.png" 2>/dev/null || true
    sips -z 256 256 "$ICON_SRC" --out "${ICON_SET}/icon_256x256.png" 2>/dev/null || true
    sips -z 512 512 "$ICON_SRC" --out "${ICON_SET}/icon_256x256@2x.png" 2>/dev/null || true
    sips -z 512 512 "$ICON_SRC" --out "${ICON_SET}/icon_512x512.png" 2>/dev/null || true
    sips -z 1024 1024 "$ICON_SRC" --out "${ICON_SET}/icon_512x512@2x.png" 2>/dev/null || true
    iconutil -c icns "$ICON_SET" -o "$ICON_ICNS" 2>/dev/null || true
    rm -rf "$ICON_SET"
fi

# Ad-hoc code sign
echo "==> Code signing (ad-hoc)"
codesign -s - --deep --force "${APP_DIR}" 2>/dev/null || true

# Build DMG
echo "==> Creating .dmg"
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -R "${APP_DIR}" "${STAGING}/"
ln -s /Applications "${STAGING}/Applications"

# Use hdiutil (mount-free approach)
hdiutil makehybrid -hfs -hfs-volume-name "${APP_NAME}" \
    -o "/tmp/celebi-hybrid.dmg" "${STAGING}" 2>/dev/null

rm -f "${DMG_NAME}"
hdiutil convert "/tmp/celebi-hybrid.dmg" -format UDZO -imagekey zlib-level=9 \
    -o "${DMG_NAME}" 2>/dev/null

rm -f "/tmp/celebi-hybrid.dmg"
rm -rf "$STAGING"

# Generate SHA256 checksum
sha256sum "${DMG_NAME}" > "${DMG_NAME}.sha256"

echo "==> Done: ${DMG_NAME}"
ls -lh "${DMG_NAME}"
