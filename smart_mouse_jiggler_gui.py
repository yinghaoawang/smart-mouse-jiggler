"""Smart Mouse Jiggler - GUI.

A small Tkinter front-end for smart_mouse_jiggler. It lets you configure the
idle threshold, jiggle distance, and check interval, then start/stop the
jiggler while watching live status updates.

Run with the py launcher on Windows:
    py smart_mouse_jiggler_gui.py
"""

from __future__ import annotations

import json
import os
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

import smart_mouse_jiggler as jiggler


def settings_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "SmartMouseJiggler" / "settings.json"


class JigglerController:
    """Runs the idle-detection loop on a background thread."""

    def __init__(self, on_status):
        self._on_status = on_status
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._idle_threshold = 60.0
        self._check_interval = 1.0
        self._distance = 1

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, idle_threshold: float, check_interval: float, distance: int) -> None:
        if self.running:
            return
        self._idle_threshold = idle_threshold
        self._check_interval = check_interval
        self._distance = distance
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._thread = None

    def _run(self) -> None:
        jiggler.keep_awake()
        jiggling = False
        try:
            while not self._stop.is_set():
                idle = jiggler.get_idle_seconds()
                if idle >= self._idle_threshold:
                    jiggler.jiggle(self._distance)
                    if not jiggling:
                        self._on_status("jiggling", idle)
                        jiggling = True
                    else:
                        self._on_status("jiggling", idle)
                else:
                    self._on_status("waiting", idle)
                    jiggling = False
                self._stop.wait(self._check_interval)
        finally:
            jiggler.allow_sleep()


class JigglerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Mouse Jiggler")
        self.resizable(False, False)
        self.controller = JigglerController(self._on_status_threadsafe)

        self._settings = self._load_settings()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if self.run_on_launch.get():
            self.after(0, self._on_start)

    # --- UI construction ---------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}
        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Idle before jiggling:").grid(row=0, column=0, sticky="w", **pad)
        self.idle_value = tk.StringVar(value=self._settings["idle_value"])
        self.idle_unit = tk.StringVar(value=self._settings["idle_unit"])
        ttk.Spinbox(
            frame, from_=1, to=86400, width=8, textvariable=self.idle_value
        ).grid(row=0, column=1, sticky="w", **pad)
        ttk.OptionMenu(
            frame, self.idle_unit, self._settings["idle_unit"], "seconds", "minutes", "hours"
        ).grid(row=0, column=2, sticky="w", **pad)

        ttk.Label(frame, text="Check interval (seconds):").grid(row=1, column=0, sticky="w", **pad)
        self.check_value = tk.StringVar(value=self._settings["check_value"])
        ttk.Spinbox(
            frame, from_=1, to=3600, width=8, textvariable=self.check_value
        ).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(frame, text="Jiggle distance (pixels):").grid(row=2, column=0, sticky="w", **pad)
        self.distance_value = tk.StringVar(value=self._settings["distance_value"])
        ttk.Spinbox(
            frame, from_=1, to=200, width=8, textvariable=self.distance_value
        ).grid(row=2, column=1, sticky="w", **pad)

        self.run_on_launch = tk.BooleanVar(value=self._settings["run_on_launch"])
        ttk.Checkbutton(
            frame, text="Start jiggling when the app launches", variable=self.run_on_launch
        ).grid(row=3, column=0, columnspan=3, sticky="w", **pad)

        button_row = ttk.Frame(frame)
        button_row.grid(row=4, column=0, columnspan=3, pady=(10, 4))
        self.start_button = ttk.Button(button_row, text="Start", command=self._on_start)
        self.start_button.grid(row=0, column=0, padx=6)
        self.stop_button = ttk.Button(
            button_row, text="Stop", command=self._on_stop, state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=6)

        self.status_var = tk.StringVar(value="Stopped.")
        status = ttk.Label(
            frame, textvariable=self.status_var, foreground="#555", anchor="w"
        )
        status.grid(row=5, column=0, columnspan=3, sticky="we", pady=(8, 0))

    # --- Settings persistence ------------------------------------------------

    DEFAULT_SETTINGS = {
        "idle_value": "60",
        "idle_unit": "seconds",
        "check_value": "1",
        "distance_value": "1",
        "run_on_launch": True,
    }

    def _load_settings(self) -> dict:
        settings = dict(self.DEFAULT_SETTINGS)
        try:
            with open(settings_path(), encoding="utf-8") as f:
                saved = json.load(f)
        except (OSError, ValueError):
            return settings
        for key in settings:
            if key in saved and isinstance(saved[key], type(settings[key])):
                settings[key] = saved[key]
        if settings["idle_unit"] not in ("seconds", "minutes", "hours"):
            settings["idle_unit"] = self.DEFAULT_SETTINGS["idle_unit"]
        return settings

    def _save_settings(self) -> None:
        settings = {
            "idle_value": self.idle_value.get(),
            "idle_unit": self.idle_unit.get(),
            "check_value": self.check_value.get(),
            "distance_value": self.distance_value.get(),
            "run_on_launch": self.run_on_launch.get(),
        }
        try:
            path = settings_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except OSError:
            pass  # Settings are a convenience; never block the app on them.

    # --- Event handlers ----------------------------------------------------

    def _read_config(self) -> tuple[float, float, int] | None:
        try:
            amount = float(self.idle_value.get())
            unit = self.idle_unit.get()
            multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}[unit]
            idle_threshold = amount * multiplier
            check_interval = float(self.check_value.get())
            distance = int(float(self.distance_value.get()))
            if idle_threshold <= 0 or check_interval <= 0 or distance <= 0:
                raise ValueError
        except (ValueError, KeyError):
            messagebox.showerror(
                "Invalid input",
                "Please enter positive numbers for idle time, check interval, "
                "and distance.",
            )
            return None
        return idle_threshold, check_interval, distance

    def _on_start(self) -> None:
        config = self._read_config()
        if config is None:
            return
        idle_threshold, check_interval, distance = config
        self._save_settings()
        self.controller.start(idle_threshold, check_interval, distance)
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("Running - waiting for inactivity...")

    def _on_stop(self) -> None:
        self.controller.stop()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Stopped.")

    def _on_status_threadsafe(self, state: str, idle: float) -> None:
        # Called from the worker thread; marshal back to the UI thread.
        self.after(0, self._update_status, state, idle)

    def _update_status(self, state: str, idle: float) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        if state == "jiggling":
            self.status_var.set(f"[{timestamp}] Idle {idle:.0f}s - jiggling to stay awake.")
        else:
            self.status_var.set(f"[{timestamp}] Active ({idle:.0f}s idle) - jiggle paused.")

    def _on_close(self) -> None:
        self._save_settings()
        self.controller.stop()
        self.destroy()


def main() -> int:
    import sys

    if not sys.platform.startswith("win"):
        print("This program only supports Windows.", file=sys.stderr)
        return 1
    app = JigglerApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
