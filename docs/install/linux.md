# Install on Linux

## Download

Download the latest `.deb` package from [GitHub Releases](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest).

## Install with dpkg

```bash
sudo dpkg -i celebi_0.1.0_amd64.deb
sudo apt-get install -f  # fix any missing dependencies
```

## Install with apt (from local file)

```bash
sudo apt install ./celebi_0.1.0_amd64.deb
```

## Launch

```bash
# From terminal
celebi

# Or find it in your application launcher
```

## Verify Installation

```bash
# Verify the proxy starts
curl http://localhost:8000/
# Expected: {"message":"Hello Traveller"}
```

## Dependencies

The `.deb` package requires these system libraries (usually pre-installed):

- `libegl1` — EGL rendering
- `libgl1` — OpenGL
- `libxkbcommon0` — keyboard handling
- `libdbus-1-3` — D-Bus IPC

## Uninstall

```bash
sudo dpkg -r celebi
```

Optionally remove the config directory:

```bash
rm -rf ~/.celebi
```
