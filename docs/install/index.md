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

| Platform | Installer |
|----------|-----------|
| **macOS** | [celebi-0.1.0-macos.dmg](https://github.com/RjyavardhanSingh/celebi-harness/releases/download/v0.1.0/celebi-0.1.0-macos.dmg) |
| **Linux** | [celebi_0.1.0_amd64.deb](https://github.com/RjyavardhanSingh/celebi-harness/releases/download/v0.1.0/celebi_0.1.0_amd64.deb) |
| **Windows** | [celebi-0.1.0-windows-setup.exe](https://github.com/RjyavardhanSingh/celebi-harness/releases/download/v0.1.0/celebi-0.1.0-windows-setup.exe) |

---

## Verifying Downloads

Each release includes SHA256 checksums. Verify your download:

```bash
# Linux / macOS
sha256sum -c celebi-<version>-<platform>.sha256

# Windows (PowerShell)
Get-FileHash celebi-*-windows-setup.exe -Algorithm SHA256
```
