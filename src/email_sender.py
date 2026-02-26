"""Send HTML emails via SMTP."""

import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from .config import Config

logger = logging.getLogger(__name__)


def send_email(subject: str, html_body: str) -> None:
    """Send an HTML email to all configured recipients."""
    Config.validate()

    recipients = Config.get_recipients()
    if not recipients:
        raise ValueError("RECIPIENT_EMAIL is empty")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")

    sender_name = Config.SENDER_NAME or Config.SMTP_USERNAME
    if sender_name and "@" not in sender_name:
        msg["From"] = formataddr((str(Header(sender_name, "utf-8")), Config.SENDER_EMAIL))
    else:
        msg["From"] = Config.SENDER_EMAIL

    msg["To"] = ", ".join(recipients)

    plain_text = (
        "您的邮件客户端不支持 HTML 格式，请使用支持 HTML 的客户端查看此邮件。"
    )
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    smtp_login = Config.get_smtp_login()
    logger.info(
        "Connecting to %s:%s (SSL=%s), login=%s ...",
        Config.SMTP_HOST,
        Config.SMTP_PORT,
        Config.SMTP_USE_SSL,
        smtp_login,
    )

    if Config.SMTP_USE_SSL:
        server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=30)
    else:
        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=30)
        server.starttls()

    try:
        server.login(smtp_login, Config.SMTP_PASSWORD)
        server.sendmail(Config.SENDER_EMAIL, recipients, msg.as_string())
        logger.info("Email sent to %s", ", ".join(recipients))
    finally:
        server.quit()
