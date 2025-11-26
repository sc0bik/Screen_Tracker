import platform
import threading
import time
from datetime import datetime
from pathlib import Path

from .config import AppConfig, config_path, load_config
from .emailer import send_email
from .i18n import t
from .notifications import Notifier
from .reporting import format_report_localized
from .scheduler import Scheduler
from .screenshots import take_screenshot
from .tracker import ActivityTracker
from .tray import start_tray


class ScreenTimeApp:
    def __init__(self, config_file: Path | None = None) -> None:
        path = config_file or config_path()
        self.config: AppConfig = load_config(path)
        self.data_dir = Path(self.config.data_dir)
        self.screenshot_dir = Path(self.config.screenshot_dir)
        self.tracker = ActivityTracker(self.config.idle_minutes, self.data_dir)
        self.scheduler = Scheduler()
        self.notifier = Notifier()
        self.running = False
        self._soft_limit_notified = False
        self._hard_limit_notified = False
        self._warning_notified = False
        self._break_notice_bucket = 0
        self.icon = None

    def start(self) -> None:
        self.running = True
        self.tracker.start()
        self._setup_schedule()
        self.icon = start_tray(self.send_daily_report, self.stop, self.data_dir, self.config.language)
        self.scheduler.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.running = False
        self.scheduler.stop()
        self.tracker.stop()

    def _setup_schedule(self) -> None:
        self.scheduler.every_day_at(self.config.report_time, self.send_daily_report)
        if self.config.screenshot_enabled:
            self.scheduler.every_hour(self._screenshot_job)
        self.scheduler.every_minutes(5, self._soft_limit_job)
        self.scheduler.every_minutes(5, self._break_reminder_job)
        self.scheduler.every_day_at("00:05", self._reset_daily_flags)

    def _screenshot_job(self) -> None:
        try:
            path = take_screenshot(self.screenshot_dir)
            self.notifier.notify(
                t("notify_screenshot_title", self.config.language),
                t("notify_screenshot_body", self.config.language, filename=path.name),
            )
        except Exception:
            pass

    def _soft_limit_job(self) -> None:
        snap = self.tracker.snapshot()
        minutes = snap.active_seconds / 60
        if not self._warning_notified and minutes >= self.config.warning_minutes:
            self.notifier.notify(
                t("notify_warning_title", self.config.language),
                t("notify_warning_body", self.config.language),
            )
            self._warning_notified = True
        if not self._soft_limit_notified and minutes >= self.config.soft_limit_minutes:
            self.notifier.notify(
                t("notify_soft_limit_title", self.config.language),
                t("notify_soft_limit_body", self.config.language),
            )
            self._soft_limit_notified = True
        if not self._hard_limit_notified and minutes >= self.config.hard_limit_minutes:
            self.notifier.notify(
                t("notify_hard_limit_title", self.config.language),
                t("notify_hard_limit_body", self.config.language),
            )
            self._hard_limit_notified = True

    def _break_reminder_job(self) -> None:
        snap = self.tracker.snapshot()
        if self.config.break_interval_minutes <= 0:
            return
        bucket = int(snap.active_seconds // (self.config.break_interval_minutes * 60))
        if bucket > self._break_notice_bucket:
            self._break_notice_bucket = bucket
            self.notifier.notify(
                t("notify_break_title", self.config.language),
                t("notify_break_body", self.config.language),
            )

    def _reset_daily_flags(self) -> None:
        self._soft_limit_notified = False
        self._hard_limit_notified = False
        self._warning_notified = False
        self._break_notice_bucket = 0

    def send_daily_report(self) -> None:
        snap = self.tracker.snapshot()
        body = format_report_localized(snap, self.config.language)
        subject = t("email_subject", self.config.language, date=snap.day.isoformat())
        try:
            send_email(self.config, subject, body)
            self.notifier.notify(
                t("notify_report_sent_title", self.config.language),
                t("notify_report_sent_body", self.config.language),
            )
        except Exception:
            self.notifier.notify(
                t("notify_report_failed_title", self.config.language),
                t("notify_report_failed_body", self.config.language),
            )
