# chat_webhook.py
import requests
from flask import current_app


def post_chat(text):
    url = current_app.config.get("GOOGLE_CHAT_WEBHOOK")
    if not url:
        return
    requests.post(url, json={"text": text}, timeout=5)
