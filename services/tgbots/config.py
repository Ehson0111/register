import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BRIDGE_SECRET = os.getenv("TELEGRAM_BRIDGE_SECRET", "crm-telegram-bridge-2026").strip()
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://chat-service:8010").rstrip("/")
POLL_INTERVAL = float(os.getenv("TELEGRAM_POLL_INTERVAL", "1.0"))
OUTBOUND_LIMIT = int(os.getenv("TELEGRAM_OUTBOUND_LIMIT", "100"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
WELCOME_TEXT = os.getenv(
    "TELEGRAM_WELCOME_TEXT",
    "Привет! Это CRM-бот. Напишите сообщение, и менеджер ответит вам в этом чате.",
)
