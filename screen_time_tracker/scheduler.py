import threading
import time
from typing import Callable

import schedule


class Scheduler:
    def __init__(self) -> None:
        self.running = False

    def every_day_at(self, hhmm: str, job: Callable) -> None:
        schedule.every().day.at(hhmm).do(job)

    def every_hour(self, job: Callable) -> None:
        schedule.every().hour.do(job)

    def every_minutes(self, minutes: int, job: Callable) -> None:
        schedule.every(minutes).minutes.do(job)

    def start(self) -> None:
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self.running = False

    def _loop(self) -> None:
        while self.running:
            schedule.run_pending()
            time.sleep(30)
