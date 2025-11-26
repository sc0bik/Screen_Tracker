import os
import sys
from pathlib import Path


def main():
    startup = Path(os.environ.get("APPDATA", "")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    repo_root = Path(__file__).resolve().parent.parent
    target_script = repo_root / "main.py"
    if not target_script.exists():
        raise FileNotFoundError(f"Cannot find main.py at {target_script}")

    bat_path = startup / "screen_time_tracker.bat"
    bat_content = f'@echo off\n"{sys.executable}" "{target_script}"\n'
    startup.mkdir(parents=True, exist_ok=True)
    bat_path.write_text(bat_content, encoding="utf-8")
    print(f"Autostart installed: {bat_path}")


if __name__ == "__main__":
    main()
