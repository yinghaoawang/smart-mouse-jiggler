"""Smart Mouse Jiggler.

Detects real user inactivity (keyboard + mouse) using the Windows
GetLastInputInfo API and only nudges the mouse when the configured idle
threshold has been exceeded. This keeps the device awake during periods of
genuine inactivity without interfering while you are actually working.

Usage examples:
    python smart_mouse_jiggler.py                 # default: jiggle after 60s idle
    python smart_mouse_jiggler.py --idle 5m       # jiggle after 5 minutes idle
    python smart_mouse_jiggler.py --idle 30s      # jiggle after 30 seconds idle
    python smart_mouse_jiggler.py --distance 3    # move 3 pixels each jiggle
    python smart_mouse_jiggler.py --check 2       # re-check idle state every 2s
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wintypes
import re
import sys
import time
from datetime import datetime

# --- Windows API setup -------------------------------------------------------

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_idle_seconds() -> float:
    """Return the number of seconds since the last keyboard or mouse input."""
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    # GetTickCount wraps roughly every 49.7 days; handle the wrap gracefully.
    millis_now = kernel32.GetTickCount()
    elapsed = (millis_now - info.dwTime) & 0xFFFFFFFF
    return elapsed / 1000.0


def get_cursor_pos() -> tuple[int, int]:
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def move_cursor(x: int, y: int) -> None:
    user32.SetCursorPos(int(x), int(y))


def jiggle(distance: int) -> None:
    """Nudge the cursor by `distance` pixels and return it to its origin."""
    x, y = get_cursor_pos()
    move_cursor(x + distance, y)
    time.sleep(0.05)
    move_cursor(x, y)


# --- Argument parsing --------------------------------------------------------

_DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([smh]?)\s*$", re.IGNORECASE)
_UNIT_SECONDS = {"": 1, "s": 1, "m": 60, "h": 3600}


def parse_duration(value: str) -> float:
    """Parse a duration like '30', '30s', '5m', or '1h' into seconds."""
    match = _DURATION_RE.match(value)
    if not match:
        raise argparse.ArgumentTypeError(
            f"invalid duration: {value!r} (use e.g. 30, 30s, 5m, 1h)"
        )
    amount, unit = match.groups()
    seconds = float(amount) * _UNIT_SECONDS[unit.lower()]
    if seconds <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return seconds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Jiggle the mouse only after a configurable period of "
        "real user inactivity to keep the device awake.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--idle",
        type=parse_duration,
        default=parse_duration("60s"),
        metavar="DURATION",
        help="idle time before jiggling (e.g. 30s, 5m, 1h)",
    )
    parser.add_argument(
        "-c",
        "--check",
        type=parse_duration,
        default=parse_duration("1s"),
        metavar="DURATION",
        help="how often to check for inactivity",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=int,
        default=1,
        help="pixels to move the cursor when jiggling",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress status output",
    )
    return parser


# --- Main loop ---------------------------------------------------------------

def _log(quiet: bool, message: str) -> None:
    if not quiet:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}", flush=True)


def run(idle_threshold: float, check_interval: float, distance: int, quiet: bool) -> None:
    _log(
        quiet,
        f"Smart Mouse Jiggler started. Jiggling after {idle_threshold:g}s idle, "
        f"checking every {check_interval:g}s. Press Ctrl+C to stop.",
    )
    jiggled_while_idle = False
    while True:
        idle = get_idle_seconds()
        if idle >= idle_threshold:
            jiggle(distance)
            if not jiggled_while_idle:
                _log(quiet, f"Idle for {idle:g}s - jiggling to keep awake.")
                jiggled_while_idle = True
        else:
            if jiggled_while_idle:
                _log(quiet, "Activity detected - pausing jiggle.")
            jiggled_while_idle = False
        time.sleep(check_interval)


def main(argv: list[str] | None = None) -> int:
    if not sys.platform.startswith("win"):
        print("This program only supports Windows.", file=sys.stderr)
        return 1

    args = build_parser().parse_args(argv)
    try:
        run(args.idle, args.check, args.distance, args.quiet)
    except KeyboardInterrupt:
        _log(args.quiet, "Stopped.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
