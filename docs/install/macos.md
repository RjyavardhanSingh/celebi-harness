# Install on macOS

## Download

Download the latest `.dmg` installer from [GitHub Releases](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest).

## Install

1. Open the downloaded `.dmg` file
2. Drag **Celebi** into the **Applications** folder
3. Eject the disk image

## First Launch

On first launch, macOS may show a security warning because the app is not notarized. To allow it:

1. Click **OK** on the warning dialog
2. Open **System Settings** → **Privacy & Security**
3. Scroll down and click **Open Anyway** next to the Celebi warning
4. Click **Open** in the confirmation dialog

Alternatively, you can bypass Gatekeeper from the terminal:

```bash
xattr -cr /Applications/Celebi.app
```

## Verify Installation

```bash
# Launch from terminal
/Applications/Celebi.app/Contents/MacOS/celebi

# Or verify the proxy starts
curl http://localhost:8000/
# Expected: {"message":"Hello Traveller"}
```

## Uninstall

1. Drag **Celebi** from Applications to Trash
2. Optionally remove the config directory:
   ```bash
   rm -rf ~/.celebi
   ```
