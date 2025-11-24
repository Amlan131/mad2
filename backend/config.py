import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis & Celery
    CELERY = dict(
        broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        task_ignore_result=False,
        timezone="Asia/Kolkata",
    )

    # Flask-Caching
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 60  # seconds

    # Schedules
    REMINDER_HOUR_IST = int(os.getenv("REMINDER_HOUR_IST", "18"))
    MONTHLY_REPORT_DAY = int(os.getenv("MONTHLY_REPORT_DAY", "1"))

    # Email / Chat
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "")
    GOOGLE_CHAT_WEBHOOK = os.getenv("GOOGLE_CHAT_WEBHOOK", "")
