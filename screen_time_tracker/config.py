import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SMTPConfig:
    host: str
    port: int
    user: str
    password: str
    use_ssl: bool = True


@dataclass
class AppConfig:
    idle_minutes: int
    report_time: str
    parent_email: str
    soft_limit_minutes: int
    hard_limit_minutes: int
    warning_minutes: int
    break_interval_minutes: int
    screenshot_enabled: bool
    screenshot_dir: str
    data_dir: str
    language: str
    smtp: SMTPConfig


def load_env_file(path: Path | None = None) -> None:
    """Populate os.environ from a simple KEY=VALUE env file if present."""
    env_path = path or Path(__file__).resolve().parent.parent / "env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
    except Exception:
        # Best effort: do not break app if env file malformed.
        pass


def _env(key: str) -> Optional[str]:
    val = os.getenv(key)
    if val is None or val == "":
        return None
    return val


def _pick(env_key: str, raw_value):
    env_val = _env(env_key)
    if env_val is not None:
        return env_val
    return raw_value


def _to_int(value) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _to_bool(value) -> Optional[bool]:
    if value is None or str(value).strip() == "":
        return None
    return str(value).lower() in {"1", "true", "yes", "on"}


def _require(value, name: str):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValueError(f"Missing required config: {name}. Set it in env file or config.json.")
    return value


def load_config(path: Path) -> AppConfig:
    # Load env file before reading environment variables.
    load_env_file(path)

    idle_minutes = _to_int(_pick("TRACKER_IDLE_MINUTES", None))
    report_time = _pick("TRACKER_REPORT_TIME", None)
    parent_email = _pick("TRACKER_PARENT_EMAIL", None)
    soft_limit = _to_int(_pick("TRACKER_SOFT_LIMIT_MINUTES", None))
    hard_limit = _to_int(_pick("TRACKER_HARD_LIMIT_MINUTES", None))
    warning_minutes = _to_int(_pick("TRACKER_WARNING_MINUTES", None))
    break_interval = _to_int(_pick("TRACKER_BREAK_INTERVAL_MINUTES", None))
    screenshot_enabled = _to_bool(_pick("TRACKER_SCREENSHOT_ENABLED", None))
    screenshot_dir = _pick("TRACKER_SCREENSHOT_DIR", None)
    data_dir = _pick("TRACKER_DATA_DIR", None)
    language = _pick("TRACKER_LANGUAGE", None)

    smtp_host = _pick("TRACKER_SMTP_HOST", None)
    smtp_port = _to_int(_pick("TRACKER_SMTP_PORT", None))
    smtp_user = _pick("TRACKER_SMTP_USER", None)
    smtp_password = _pick("TRACKER_SMTP_PASSWORD", None)
    smtp_use_ssl = _to_bool(_pick("TRACKER_SMTP_USE_SSL", None))

    hard_limit = hard_limit or soft_limit

    return AppConfig(
        idle_minutes=_require(idle_minutes, "TRACKER_IDLE_MINUTES"),
        report_time=str(_require(report_time, "TRACKER_REPORT_TIME")),
        parent_email=str(_require(parent_email, "TRACKER_PARENT_EMAIL")),
        soft_limit_minutes=_require(soft_limit, "TRACKER_SOFT_LIMIT_MINUTES"),
        hard_limit_minutes=_require(hard_limit, "TRACKER_HARD_LIMIT_MINUTES"),
        warning_minutes=_require(warning_minutes, "TRACKER_WARNING_MINUTES"),
        break_interval_minutes=_require(break_interval, "TRACKER_BREAK_INTERVAL_MINUTES"),
        screenshot_enabled=bool(_require(screenshot_enabled, "TRACKER_SCREENSHOT_ENABLED")),
        screenshot_dir=str(_require(screenshot_dir, "TRACKER_SCREENSHOT_DIR")),
        data_dir=str(_require(data_dir, "TRACKER_DATA_DIR")),
        language=str(language or "en"),
        smtp=SMTPConfig(
            host=str(_require(smtp_host, "TRACKER_SMTP_HOST")),
            port=int(_require(smtp_port, "TRACKER_SMTP_PORT")),
            user=str(_require(smtp_user, "TRACKER_SMTP_USER")),
            password=str(_require(smtp_password, "TRACKER_SMTP_PASSWORD")),
            use_ssl=bool(smtp_use_ssl if smtp_use_ssl is not None else True),
        ),
    )


def config_path() -> Path:
    env = os.getenv("TRACKER_CONFIG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "env"
