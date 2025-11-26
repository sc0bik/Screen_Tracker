"""Tiny localization helper for English/Russian UI strings."""

from __future__ import annotations

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "tray_title": "Screen Time Tracker",
        "tray_send_now": "Send report now",
        "tray_open_folder": "Open data folder",
        "tray_exit": "Exit",
        "notify_screenshot_title": "Screenshot saved",
        "notify_screenshot_body": "{filename} saved for monitoring",
        "notify_break_title": "Take a short break",
        "notify_break_body": "Stand up, stretch, and rest your eyes.",
        "notify_warning_title": "Break reminder",
        "notify_warning_body": "You have been active for a long time. Take a pause.",
        "notify_soft_limit_title": "Soft limit reached",
        "notify_soft_limit_body": "You are close to the daily cap. Wrap up soon.",
        "notify_hard_limit_title": "Hard limit reached",
        "notify_hard_limit_body": "Daily limit is over. Please stop using the computer now.",
        "notify_report_sent_title": "Report sent",
        "notify_report_sent_body": "Daily screen time report emailed.",
        "notify_report_failed_title": "Report failed",
        "notify_report_failed_body": "Could not send report. Check email settings.",
        "email_subject": "Screen time report {date}",
    },
    "ru": {
        "tray_title": "Трекер экранного времени",
        "tray_send_now": "Отправить отчет",
        "tray_open_folder": "Открыть папку данных",
        "tray_exit": "Выход",
        "notify_screenshot_title": "Скриншот сохранен",
        "notify_screenshot_body": "{filename} сохранен для мониторинга",
        "notify_break_title": "Сделай перерыв",
        "notify_break_body": "Встань, разомнись и дай глазам отдохнуть.",
        "notify_warning_title": "Пора отдохнуть",
        "notify_warning_body": "Ты давно активен. Сделай паузу.",
        "notify_soft_limit_title": "Мягкий лимит",
        "notify_soft_limit_body": "Скоро дневной предел. Завершай работу.",
        "notify_hard_limit_title": "Дневной лимит превышен",
        "notify_hard_limit_body": "Рабочий день закончен. Пора остановиться.",
        "notify_report_sent_title": "Отчет отправлен",
        "notify_report_sent_body": "Ежедневный отчет отправлен на email.",
        "notify_report_failed_title": "Ошибка отправки отчета",
        "notify_report_failed_body": "Не удалось отправить письмо. Проверь настройки.",
        "email_subject": "Отчет об экранном времени {date}",
    },
}


def t(key: str, language: str, **kwargs) -> str:
    """Translate key with optional format kwargs."""
    lang = (language or "en").lower()
    catalog = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = catalog.get(key) or TRANSLATIONS["en"].get(key) or key
    return template.format(**kwargs)
