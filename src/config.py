"""Configuration loaded from environment variables."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


class Config:
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", "465"))
    SMTP_USERNAME: str = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    SENDER_EMAIL: str = os.environ.get("SENDER_EMAIL", "")
    SENDER_NAME: str = os.environ.get("SENDER_NAME", "")
    RECIPIENT_EMAIL: str = os.environ.get("RECIPIENT_EMAIL", "")
    SMTP_USE_SSL: bool = os.environ.get("SMTP_USE_SSL", "true").lower() == "true"

    @classmethod
    def get_smtp_login(cls) -> str:
        """Return the value to use for SMTP LOGIN.

        If SMTP_USERNAME looks like an email address, use it directly.
        Otherwise (e.g. it contains a Chinese display name), fall back to
        SENDER_EMAIL which is always a valid email address.
        """
        username = cls.SMTP_USERNAME
        if username and "@" in username:
            try:
                username.encode("ascii")
                return username
            except UnicodeEncodeError:
                pass
        return cls.SENDER_EMAIL

    @classmethod
    def get_sender_display(cls) -> str:
        """Return a formatted From header value with optional display name."""
        name = cls.SENDER_NAME or cls.SMTP_USERNAME
        if name and "@" not in name:
            return f"{name} <{cls.SENDER_EMAIL}>"
        return cls.SENDER_EMAIL

    @classmethod
    def get_recipients(cls) -> list[str]:
        return [e.strip() for e in cls.RECIPIENT_EMAIL.split(",") if e.strip()]

    @classmethod
    def validate(cls) -> None:
        required = {
            "SMTP_HOST": cls.SMTP_HOST,
            "SMTP_PASSWORD": cls.SMTP_PASSWORD,
            "SENDER_EMAIL": cls.SENDER_EMAIL,
            "RECIPIENT_EMAIL": cls.RECIPIENT_EMAIL,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            print(f"[ERROR] 缺少必要的环境变量: {', '.join(missing)}", file=sys.stderr)
            print("请参考 .env.example 配置环境变量", file=sys.stderr)
            sys.exit(1)
