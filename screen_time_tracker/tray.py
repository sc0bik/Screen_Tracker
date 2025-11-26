import threading
import webbrowser
from pathlib import Path

from .i18n import t

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover - tray optional
    pystray = None
    Image = None
    ImageDraw = None


def _create_icon():
    size = (64, 64)
    image = Image.new("RGB", size, color=(40, 120, 200))
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 56, 56), outline=(255, 255, 255), width=3)
    draw.line((16, 40, 48, 40), fill=(255, 255, 255), width=3)
    draw.line((32, 24, 32, 40), fill=(255, 255, 255), width=3)
    return image


def start_tray(on_send_report, on_exit, data_dir: Path, language: str = "en"):
    if not pystray or not Image:
        return None

    icon = pystray.Icon(
        "screen_time_tracker",
        _create_icon(),
        t("tray_title", language),
        menu=pystray.Menu(
            pystray.MenuItem(
                t("tray_send_now", language),
                lambda icon, item: _run_async(on_send_report),
            ),
            pystray.MenuItem(
                t("tray_open_folder", language),
                lambda icon, item: webbrowser.open(str(data_dir)),
            ),
            pystray.MenuItem(
                t("tray_exit", language),
                lambda icon, item: _safe_exit(icon, on_exit),
            ),
        ),
    )

    threading.Thread(target=icon.run, daemon=True).start()
    return icon


def _run_async(func):
    threading.Thread(target=func, daemon=True).start()


def _safe_exit(icon, on_exit):
    try:
        icon.stop()
    finally:
        on_exit()
