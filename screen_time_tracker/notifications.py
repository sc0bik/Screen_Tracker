import platform

try:
    from win10toast import ToastNotifier
except Exception:  # pragma: no cover - used only on Windows
    ToastNotifier = None


class Notifier:
    def __init__(self) -> None:
        self.enabled = platform.system() == "Windows" and ToastNotifier is not None
        self.notifier = ToastNotifier() if self.enabled else None

    def notify(self, title: str, message: str, duration: int = 5) -> None:
        if not self.enabled:
            return
        try:
            # Use non-threaded mode to avoid Win32 WNDPROC errors in some environments.
            self.notifier.show_toast(title, message, duration=duration, threaded=False)
        except Exception:
            pass
