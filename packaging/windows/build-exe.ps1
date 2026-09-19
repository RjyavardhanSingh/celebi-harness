# Build a Windows .exe installer from a PyInstaller bundle.
#
# Usage:
#   .\build-exe.ps1 [-Version "0.1.0"]
#
# Prerequisites:
#   - PyInstaller bundle at dist\celebi\
#   - NSIS installed (choco install nsis)
#
# Output:
#   dist\celebi-<version>-windows-setup.exe
param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$AppName = "Celebi"
$NsiScript = "packaging\windows\installer.nsi"
$LicenseFile = "LICENSE.txt"
$IconFile = "assets\logo.png"

Write-Host "==> Building Windows installer for $AppName v$Version"

# Verify prerequisites
if (-not (Test-Path "dist\celebi\celebi.exe")) {
    Write-Error "PyInstaller bundle not found at dist\celebi\celebi.exe"
    exit 1
}

# Find NSIS
$nsisPath = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $nsisPath) {
    $nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
    if (-not (Test-Path $nsisPath)) {
        Write-Error "NSIS not found. Install with: choco install nsis"
        exit 1
    }
}

# Generate LICENSE.txt if it doesn't exist (NSIS requires it)
if (-not (Test-Path $LicenseFile)) {
    Write-Host "==> Creating placeholder LICENSE.txt"
    @"
MIT License

Copyright (c) 2026 Rajyavardhan Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the Software), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Set-Content $LicenseFile -Encoding UTF8
}

# Build the installer
Write-Host "==> Running NSIS"
& "$nsisPath" /V3 /DAPP_VERSION="$Version" "$NsiScript"
if ($LASTEXITCODE -ne 0) {
    Write-Error "NSIS build failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

$outputFile = "dist\celebi-$Version-windows-setup.exe"
if (Test-Path $outputFile) {
    # Generate SHA256 checksum
    $hash = Get-FileHash -Algorithm SHA256 -Path $outputFile
    "$($hash.Hash.ToLower())  $outputFile" | Set-Content "$outputFile.sha256"
    Write-Host "==> Done: $outputFile"
    Get-Item $outputFile | Select-Object Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB, 2)}}
} else {
    Write-Error "Installer not found at $outputFile"
    exit 1
}
