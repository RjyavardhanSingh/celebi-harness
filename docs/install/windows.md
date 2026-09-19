# Install on Windows

## Download

Download the latest `celebi-*-windows-setup.exe` from [GitHub Releases](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest).

## Install

1. Run the downloaded `.exe` installer
2. Click **Next** on the welcome screen
3. Accept the license agreement
4. Choose the install location (default: `C:\Program Files\Celebi`)
5. Click **Install**
6. Click **Finish** to launch Celebi

## First Launch

Windows Defender SmartScreen may show a warning because the app is not code-signed. To allow it:

1. Click **More info** on the SmartScreen dialog
2. Click **Run anyway**

## Verify Installation

```powershell
# Verify the proxy starts
Invoke-WebRequest http://localhost:8000/
# Expected: {"message":"Hello Traveller"}
```

## Uninstall

1. Open **Settings** → **Apps** → **Installed apps**
2. Find **Celebi** and click **Uninstall**
3. Follow the uninstaller prompts

Or use the uninstaller shortcut in Start Menu → Celebi → Uninstall.

Optionally remove the config directory:

```powershell
Remove-Item -Recurse -Force ~\.celebi
```
