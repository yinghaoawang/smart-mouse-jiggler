"""Build a standalone Windows .exe for the Smart Mouse Jiggler GUI.

Usage:
    py build_exe.py

This wraps PyInstaller with sensible defaults: a single-file, windowed
(no console) executable that bundles smart_mouse_jiggler_gui.py and its
dependency smart_mouse_jiggler.py.

The finished executable is written to the ``dist`` folder.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "SmartMouseJiggler"
ENTRY_SCRIPT = "smart_mouse_jiggler_gui.py"
ROOT = Path(__file__).resolve().parent


def ensure_pyinstaller() -> None:
    """Install PyInstaller if it is not already available."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found - installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"]
        )


def clean() -> None:
    """Remove previous build artifacts."""
    for folder in ("build", "dist"):
        path = ROOT / folder
        if path.exists():
            shutil.rmtree(path)
    spec = ROOT / f"{APP_NAME}.spec"
    if spec.exists():
        spec.unlink()


def build() -> int:
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        APP_NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        str(ROOT / ENTRY_SCRIPT),
    ]
    print("Running:", " ".join(args))
    result = subprocess.run(args, cwd=ROOT)
    if result.returncode == 0:
        exe = ROOT / "dist" / f"{APP_NAME}.exe"
        print(f"\nBuild complete: {exe}")
    return result.returncode


def main() -> int:
    if not sys.platform.startswith("win"):
        print("This builder targets Windows.", file=sys.stderr)
        return 1
    ensure_pyinstaller()
    clean()
    return build()


if __name__ == "__main__":
    raise SystemExit(main())
