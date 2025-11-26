from datetime import datetime
from pathlib import Path

try:
    from PIL import ImageGrab
except Exception:  # pragma: no cover - optional
    ImageGrab = None


def take_screenshot(base_dir: Path) -> Path:
    if not ImageGrab:
        raise RuntimeError("Pillow ImageGrab is not available on this platform.")
    now = datetime.now()
    day_dir = base_dir / now.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    filename = now.strftime("%H-%M-%S.png")
    path = day_dir / filename
    image = ImageGrab.grab()
    image.save(path)
    return path
