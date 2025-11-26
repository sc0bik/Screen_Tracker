import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from .config import AppConfig


def send_email(config: AppConfig, subject: str, body: str, to: Optional[str] = None) -> None:
    recipient = to or config.parent_email
    msg = EmailMessage()
    msg["From"] = config.smtp.user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    if config.smtp.use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config.smtp.host, config.smtp.port, context=context) as server:
            server.login(config.smtp.user, config.smtp.password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(config.smtp.host, config.smtp.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(config.smtp.user, config.smtp.password)
            server.send_message(msg)
