from datetime import date, timedelta
from typing import Dict, Tuple

from .tracker import ActivitySnapshot


def seconds_to_hours_minutes(seconds: float) -> Tuple[int, int]:
    minutes = int(seconds // 60)
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return hours, remaining_minutes


def format_report(snapshot: ActivitySnapshot) -> str:
    hours, minutes = seconds_to_hours_minutes(snapshot.active_seconds)
    lines = []
    lines.append(f"За сегодня, {snapshot.day.isoformat()}, общее активное время: {hours} часов {minutes} минут.")
    lines.append("")
    lines.append("По приложениям:")
    per_app = snapshot.per_app_seconds or {}
    if per_app:
        for app, seconds in sorted(per_app.items(), key=lambda item: item[1], reverse=True):
            h, m = seconds_to_hours_minutes(seconds)
            lines.append(f"- {app}: {h}ч {m}м")
    else:
        lines.append("- Нет данных")
    return "\n".join(lines)


def format_report_en(snapshot: ActivitySnapshot) -> str:
    hours, minutes = seconds_to_hours_minutes(snapshot.active_seconds)
    lines = []
    lines.append(f"Today ({snapshot.day.isoformat()}) active time: {hours} hours {minutes} minutes.")
    lines.append("")
    lines.append("Per application:")
    per_app = snapshot.per_app_seconds or {}
    if per_app:
        for app, seconds in sorted(per_app.items(), key=lambda item: item[1], reverse=True):
            h, m = seconds_to_hours_minutes(seconds)
            lines.append(f"- {app}: {h}h {m}m")
    else:
        lines.append("- No data")
    return "\n".join(lines)


def format_report_localized(snapshot: ActivitySnapshot, language: str) -> str:
    lang = (language or "en").lower()
    if lang == "ru":
        return format_report(snapshot)
    if lang == "en":
        return format_report_en(snapshot)
    # Default to bilingual if unknown or "both"
    ru_body = format_report(snapshot)
    en_body = format_report_en(snapshot)
    return f"{ru_body}\n\n----\nEnglish version:\n{en_body}"
