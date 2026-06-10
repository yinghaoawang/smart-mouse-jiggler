# Smart Mouse Jiggler

A lightweight Windows utility that keeps your device awake by jiggling the mouse
**only when you are actually inactive**. It uses the Windows `GetLastInputInfo`
API to measure real keyboard and mouse idle time, so it never fights you while
you're working — it only kicks in after a configurable period of no activity.

## Features

- Detects genuine inactivity (keyboard **and** mouse), not just elapsed time.
- Configurable idle threshold in seconds, minutes, or hours.
- Tiny cursor nudge that returns to the original position.
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
