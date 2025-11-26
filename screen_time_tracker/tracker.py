import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import platform

import psutil

try:
    import win32gui
    import win32process
except Exception:  # pragma: no cover - used only on Windows
    win32gui = None
    win32process = None

try:
    from pynput import keyboard, mouse
except ImportError:  # pragma: no cover - optional for environments without pynput
    keyboard = None
    mouse = None


@dataclass
class ActivitySnapshot:
    active_seconds: float
    per_app_seconds: Dict[str, float]
    day: date


class ActivityTracker:
    def __init__(self, idle_minutes: int, data_dir: Path):
        self.idle_threshold = timedelta(minutes=idle_minutes)
        self.last_activity: datetime = datetime.now()
        self.last_tick: datetime = datetime.now()
        self.active_seconds_today: float = 0.0
        self.per_app_seconds: Dict[str, float] = defaultdict(float)
        self.running = False
        self.lock = threading.Lock()
        self.current_day = date.today()
        self.data_dir = data_dir
        self.listeners = []

    def start(self) -> None:
        self.running = True
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._start_listeners()
        threading.Thread(target=self._tick_loop, daemon=True).start()

    def stop(self) -> None:
        self.running = False
        for listener in self.listeners:
            try:
                listener.stop()
            except Exception:
                continue

    def _start_listeners(self) -> None:
        if keyboard:
            kb_listener = keyboard.Listener(on_press=self._on_input, on_release=self._on_input)
            kb_listener.start()
            self.listeners.append(kb_listener)
        if mouse:
            mouse_listener = mouse.Listener(on_move=self._on_input, on_click=self._on_input, on_scroll=self._on_input)
            mouse_listener.start()
            self.listeners.append(mouse_listener)

    def _on_input(self, *args, **kwargs):
        self.last_activity = datetime.now()

    def _tick_loop(self) -> None:
        while self.running:
            self._tick()
            time.sleep(1)

    def _tick(self) -> None:
        now = datetime.now()
        idle = (now - self.last_activity) > self.idle_threshold
        delta = (now - self.last_tick).total_seconds()
        if delta < 0:
            delta = 0
        if now.date() != self.current_day:
            self._rollover(now.date())
        if not idle:
            app_name = self._active_app_name()
            with self.lock:
                self.active_seconds_today += delta
                self.per_app_seconds[app_name] += delta
        self.last_tick = now

    def _rollover(self, new_day: date) -> None:
        with self.lock:
            self._persist_day()
            self.active_seconds_today = 0.0
            self.per_app_seconds = defaultdict(float)
            self.current_day = new_day

    def _persist_day(self) -> None:
        import json

        data = {
            "day": self.current_day.isoformat(),
            "active_seconds": self.active_seconds_today,
            "per_app": self.per_app_seconds,
        }
        path = self.data_dir / f"{self.current_day.isoformat()}.json"
        try:
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            # Best effort; avoid crashing tracker
            pass

    def _active_app_name(self) -> str:
        if platform.system() != "Windows" or not win32gui or not win32process:
            return "unknown"
        try:
            hwnd = win32gui.GetForegroundWindow()
            thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            name = proc.name()
            window_title = win32gui.GetWindowText(hwnd)
            if window_title:
                return f"{name} - {window_title[:40]}"
            return name
        except Exception:
            return "unknown"

    def snapshot(self) -> ActivitySnapshot:
        with self.lock:
            return ActivitySnapshot(
                active_seconds=self.active_seconds_today,
                per_app_seconds=dict(self.per_app_seconds),
                day=self.current_day,
            )

    def reset_today(self) -> None:
        with self.lock:
            self.active_seconds_today = 0.0
            self.per_app_seconds = defaultdict(float)
            self.current_day = date.today()
