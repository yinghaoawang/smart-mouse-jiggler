# Smart Mouse Jiggler

A lightweight Windows utility that keeps your device awake by jiggling the mouse
**only when you are actually inactive**. It uses the Windows `GetLastInputInfo`
API to measure real keyboard and mouse idle time, so it never fights you while
you're working — it only kicks in after a configurable period of no activity.

## Features

- Detects genuine inactivity (keyboard **and** mouse), not just elapsed time.
- Configurable idle threshold in seconds, minutes, or hours.
- Tiny cursor nudge that returns to the original position.
- GUI settings are saved to `%APPDATA%\SmartMouseJiggler\settings.json` and
  restored on the next launch.
- Optional "Start jiggling when the app launches" checkbox in the GUI.
- One-click scripts to run the app automatically at Windows startup.
- No third-party dependencies — pure Python standard library + Windows API.

## Requirements

- Windows
- Python 3.9+

## Usage

```powershell
# Jiggle after 60 seconds of inactivity (default)
python smart_mouse_jiggler.py

# Jiggle after 5 minutes of inactivity
python smart_mouse_jiggler.py --idle 5m

# Jiggle after 30 seconds, moving the cursor 3 pixels each time
python smart_mouse_jiggler.py --idle 30s --distance 3

# Check the idle state every 2 seconds
python smart_mouse_jiggler.py --idle 2m --check 2s

# Run silently
python smart_mouse_jiggler.py --idle 5m --quiet
```

Press `Ctrl+C` to stop.

## Run at Windows startup

Double-click `add_to_startup.bat` to add the app to your startup programs. It
creates a shortcut in the current user's Startup folder that launches the GUI:

- If a built executable exists (`dist\SmartMouseJiggler.exe` from
  `py build_exe.py`), the shortcut points at it.
- Otherwise it launches `smart_mouse_jiggler_gui.py` with `pyw.exe`/`pythonw.exe`
  (no console window).

To undo, double-click `remove_from_startup.bat`.

Tip: leave the GUI's "Start jiggling when the app launches" checkbox enabled so
the jiggler is active immediately after login with your saved settings.

## Options

| Option            | Description                                          | Default |
| ----------------- | ---------------------------------------------------- | ------- |
| `-i`, `--idle`    | Idle time before jiggling (e.g. `30s`, `5m`, `1h`).  | `60s`   |
| `-c`, `--check`   | How often to check for inactivity.                   | `1s`    |
| `-d`, `--distance`| Pixels to move the cursor when jiggling.             | `1`     |
| `-q`, `--quiet`   | Suppress status output.                              | off     |

## How it works

The program polls `GetLastInputInfo` to find how long it has been since your last
input. When that idle time exceeds your configured threshold, it nudges the
cursor by a few pixels and moves it back. The moment you touch the keyboard or
mouse again, the idle timer resets and jiggling pauses automatically.
