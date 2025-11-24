# email_utils.py
import smtplib
from email.mime.text import MIMEText
from flask import current_app


def send_email(to, subject, html):
    host = current_app.config.get("SMTP_HOST")
    if not host:
        return
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = current_app.config.get("FROM_EMAIL")
    msg["To"] = to
    with smtplib.SMTP(host, current_app.config.get("SMTP_PORT", 587)) as s:
        s.starttls()
        s.login(current_app.config.get("SMTP_USER"),
                current_app.config.get("SMTP_PASS"))
        s.sendmail(msg["From"], [to], msg.as_string())
