# Install Celebi

Choose your platform below to install Celebi.

<div id="platform-detect" style="display:none; margin: 1em 0; padding: 1em; border: 1px solid #4FC3F7; border-radius: 8px; background: #1e1e2e;">
  <strong>Your platform: <span id="detected-platform"></span></strong>
  <p id="recommended-action"></p>
</div>

<script>
  (function() {
    var ua = navigator.userAgent.toLowerCase();
    var platform = document.getElementById('detected-platform');
    var action = document.getElementById('recommended-action');
    var box = document.getElementById('platform-detect');

    var os = 'unknown';
    if (ua.includes('mac')) os = 'macOS';
    else if (ua.includes('linux')) os = 'Linux';
    else if (ua.includes('win')) os = 'Windows';

    if (os !== 'unknown') {
      box.style.display = 'block';
      platform.textContent = os;
      if (os === 'macOS') {
        action.innerHTML = 'Recommended: <a href="macos.md">Install on macOS</a> — download the .dmg installer.';
      } else if (os === 'Linux') {
        action.innerHTML = 'Recommended: <a href="linux.md">Install on Linux</a> — download the .deb package.';
      } else if (os === 'Windows') {
        action.innerHTML = 'Recommended: <a href="windows.md">Install on Windows</a> — download the .exe installer.';
      }
    }
  })();
</script>

---

## All Platforms

| Platform | Format | Guide |
|----------|--------|-------|
| macOS (Apple Silicon / Intel) | `.dmg` disk image | [macOS Install Guide](macos.md) |
| Linux (Debian / Ubuntu) | `.deb` package | [Linux Install Guide](linux.md) |
| Windows (x64) | `.exe` installer | [Windows Install Guide](windows.md) |

---

## Verifying Downloads

Each release includes SHA256 checksums. Verify your download:

```bash
# Linux / macOS
sha256sum -c celebi-<version>-<platform>.sha256

# Windows (PowerShell)
Get-FileHash celebi-*-windows-setup.exe -Algorithm SHA256
```
