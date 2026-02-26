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
    RECIPIENT_EMAIL: str = os.environ.get("RECIPIENT_EMAIL", "")
    SMTP_USE_SSL: bool = os.environ.get("SMTP_USE_SSL", "true").lower() == "true"

    @classmethod
    def get_recipients(cls) -> list[str]:
        return [e.strip() for e in cls.RECIPIENT_EMAIL.split(",") if e.strip()]

    @classmethod
    def validate(cls) -> None:
        required = {
            "SMTP_HOST": cls.SMTP_HOST,
            "SMTP_USERNAME": cls.SMTP_USERNAME,
            "SMTP_PASSWORD": cls.SMTP_PASSWORD,
            "SENDER_EMAIL": cls.SENDER_EMAIL,
            "RECIPIENT_EMAIL": cls.RECIPIENT_EMAIL,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            print(f"[ERROR] 缺少必要的环境变量: {', '.join(missing)}", file=sys.stderr)
            print("请参考 .env.example 配置环境变量", file=sys.stderr)
            sys.exit(1)
