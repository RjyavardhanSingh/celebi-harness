"""Cross-platform build script for Celebi desktop app.

Usage:
    python build.py

Produces a standalone directory in dist/celebi/ containing the executable.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    dist = root / "dist"
    spec_file = root / "celebi.spec"

    if not spec_file.exists():
        print(f"Error: {spec_file} not found")
        sys.exit(1)

    # Clean previous builds
    build_dir = root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist.exists():
        shutil.rmtree(dist)

    print(f"Building Celebi for {platform.system()} ({platform.machine()})...")
    print(f"Python: {sys.version}")

    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]

    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode != 0:
        print("PyInstaller build failed!")
        sys.exit(1)

    # Verify output
    celebi_dist = dist / "celebi"
    if not celebi_dist.exists():
        print(f"Error: Expected output at {celebi_dist} not found")
        sys.exit(1)

    # Report output
    if platform.system() == "Windows":
        exe = celebi_dist / "celebi.exe"
    else:
        exe = celebi_dist / "celebi"

    if exe.exists():
        size_mb = exe.stat().st_size / (1024 * 1024)
        print("\nBuild successful!")
        print(f"Executable: {exe}")
        print(f"Size: {size_mb:.1f} MB")
        print("\nTo run:")
        print(f"  {exe}")
    else:
        print(f"\nBuild completed. Output directory: {celebi_dist}")

    # Show directory contents
    print(f"\nContents of {celebi_dist}:")
    for item in sorted(celebi_dist.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            if size > 1024 * 1024:
                print(f"  {item.name:40s} {size / 1024 / 1024:.1f} MB")
            elif size > 1024:
                print(f"  {item.name:40s} {size / 1024:.1f} KB")
            else:
                print(f"  {item.name:40s} {size} B")


if __name__ == "__main__":
    main()
