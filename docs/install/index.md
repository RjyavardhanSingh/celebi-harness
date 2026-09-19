# Install Celebi

Choose your platform below to install Celebi.

---

## All Platforms

| Platform | Format | Guide |
|----------|--------|-------|
| macOS (Apple Silicon / Intel) | `.dmg` disk image | [macOS Install Guide](macos.md) |
| Linux (Debian / Ubuntu) | `.deb` package | [Linux Install Guide](linux.md) |
| Windows (x64) | `.exe` installer | [Windows Install Guide](windows.md) |

---

## Download

Go to [**GitHub Releases**](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) to download the latest installer for your platform.

| Platform | File |
|----------|------|
| **macOS** | `celebi-*-macos.dmg` |
| **Linux** | `celebi_*_amd64.deb` |
| **Windows** | `celebi-*-windows-setup.exe` |

Each release includes SHA256 checksums (`.sha256` files) for verification.

---

## Verifying Downloads

```bash
# Linux / macOS
sha256sum -c celebi-<version>-<platform>.sha256

# Windows (PowerShell)
Get-FileHash celebi-*-windows-setup.exe -Algorithm SHA256
```
