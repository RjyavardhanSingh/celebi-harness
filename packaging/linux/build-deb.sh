#!/usr/bin/env bash
# Build a .deb package from a PyInstaller bundle.
#
# Usage:
#   ./build-deb.sh [version]
#
# Prerequisites:
#   - PyInstaller bundle at dist/celebi/
#   - dpkg-deb, fakeroot (install via: sudo apt-get install fakeroot dpkg-dev)
#
# Output:
#   dist/celebi-<version>-linux-amd64.deb
set -euo pipefail

VERSION="${1:-0.1.0}"
PACKAGE="celebi"
ARCH="amd64"
DEB_NAME="${PACKAGE}_${VERSION}_${ARCH}"
DEB_DIR="dist/${DEB_NAME}"
BUNDLE_DIR="dist/celebi"

echo "==> Building .deb package"

# Clean previous artifacts
rm -rf "${DEB_DIR}"
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/opt/${PACKAGE}"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps"

# Copy PyInstaller bundle
cp -R "${BUNDLE_DIR}/"* "${DEB_DIR}/opt/${PACKAGE}/"

# Make the main binary executable
chmod +x "${DEB_DIR}/opt/${PACKAGE}/celebi"

# Create symlink in /usr/bin
ln -s "/opt/${PACKAGE}/celebi" "${DEB_DIR}/usr/bin/celebi"

# Copy icon
if [ -f "assets/logo.png" ]; then
    cp "assets/logo.png" "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps/celebi.png"
fi

# Create .desktop file
cat > "${DEB_DIR}/usr/share/applications/celebi.desktop" << EOF
[Desktop Entry]
Name=Celebi
Comment=LLM Time Travel Harness
Exec=/opt/${PACKAGE}/celebi
Icon=celebi
Type=Application
Categories=Development;Utility;
Terminal=false
StartupWMClass=celebi
EOF

# Calculate installed size (in KB)
INSTALLED_SIZE=$(du -sk "${DEB_DIR}" | cut -f1)

# Create DEBIAN/control
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: ${PACKAGE}
Version: ${VERSION}
Section: devel
Priority: optional
Architecture: ${ARCH}
Depends: libegl1, libgl1, libxkbcommon0, libdbus-1-3
Installed-Size: ${INSTALLED_SIZE}
Maintainer: Rajyavardhan Singh <rajyavardhan@users.noreply.github.com>
Description: LLM Time Travel Harness
 Celebi is a man-in-the-middle proxy that captures every
 request/response pair between your coding agent and LLM providers,
 forming a timeline of conversations you can visualize, search, and replay.
Homepage: https://github.com/RjyavardhanSingh/celebi-harness
EOF

# Build the .deb
echo "==> Packaging with dpkg-deb"
fakeroot dpkg-deb --build "${DEB_DIR}" "dist/${DEB_NAME}.deb"

# Generate SHA256 checksum
sha256sum "dist/${DEB_NAME}.deb" > "dist/${DEB_NAME}.deb.sha256"

echo "==> Done: dist/${DEB_NAME}.deb"
ls -lh "dist/${DEB_NAME}.deb"
