import logging
import os
import time
from typing import Any, Dict, List

import requests


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("tg-bridge-bot")


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8795868534:AAGhWziwIb7xFA-SFQ-VXh59Vfl9otrvDvg")
BRIDGE_SECRET = os.getenv("TELEGRAM_BRIDGE_SECRET", "crm-telegram-bridge-2026")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://chat-service:8010")
POLL_TIMEOUT = int(os.getenv("TELEGRAM_POLL_TIMEOUT", "5"))
IDLE_SLEEP = float(os.getenv("TELEGRAM_IDLE_SLEEP", "0.4"))
WELCOME_TEXT = os.getenv(
    "TELEGRAM_WELCOME_TEXT",
    "Привет! Это CRM-бот. Напишите сообщение, и менеджер ответит вам в этом чате.",
)

INBOUND_URL = f"{CHAT_SERVICE_URL}/api/chat/telegram/inbound/"
OUTBOUND_URL = f"{CHAT_SERVICE_URL}/api/chat/telegram/outbound/"


def _headers() -> Dict[str, str]:
    return {"X-Telegram-Bridge-Secret": BRIDGE_SECRET, "Content-Type": "application/json"}


def ensure_configuration() -> bool:
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set; bot is idle")
        return False
    if not BRIDGE_SECRET:
        logger.warning("TELEGRAM_BRIDGE_SECRET is not set; bot is idle")
        return False
    return True


def tg_request(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    tg_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    resp = requests.post(f"{tg_api_url}/{method}", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error in {method}: {data}")
    return data


def fetch_updates(offset: int) -> List[Dict[str, Any]]:
    payload = {"timeout": POLL_TIMEOUT, "offset": offset}
    data = tg_request("getUpdates", payload)
    return data.get("result", [])


def send_welcome_message(chat_id: int) -> None:
    tg_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": WELCOME_TEXT[:4000],
        },
    )


def forward_user_message_to_chatservice(message: Dict[str, Any]) -> None:
    chat = message.get("chat") or {}
    from_user = message.get("from") or {}
    text = (message.get("text") or "").strip()
    if not text:
        return
    if chat.get("type") != "private":
        return
    if text.lower().strip() == "/start":
        send_welcome_message(int(chat.get("id")))
        return

    payload = {
        "chat_id": chat.get("id"),
        "text": text,
        "username": from_user.get("username", "") or "",
        "first_name": from_user.get("first_name", "") or "",
        "last_name": from_user.get("last_name", "") or "",
    }
    resp = requests.post(INBOUND_URL, json=payload, headers=_headers(), timeout=30)
    if resp.status_code >= 300:
        logger.error("Failed to forward inbound Telegram message: %s %s", resp.status_code, resp.text)
        return
    logger.info("Inbound Telegram message delivered: chat_id=%s", payload["chat_id"])


def send_outbound_manager_replies() -> None:
    resp = requests.get(OUTBOUND_URL, params={"limit": 100}, headers=_headers(), timeout=30)
    if resp.status_code >= 300:
        logger.error("Failed to fetch outbound manager replies: %s %s", resp.status_code, resp.text)
        return
    messages = (resp.json() or {}).get("messages", [])
    for item in messages:
        text = item.get("text", "")
        sender_name = item.get("sender_name", "Менеджер")
        formatted = f"{sender_name}:\n{text}"
        try:
            tg_request(
                "sendMessage",
                {
                    "chat_id": item["chat_id"],
                    "text": formatted[:4000],
                },
            )
            logger.info(
                "Outbound manager message sent to Telegram: chat_id=%s message_id=%s",
                item.get("chat_id"),
                item.get("message_id"),
            )
        except Exception as exc:
            logger.exception("Failed to send outbound message to Telegram: %s", exc)


def main() -> None:
    if not ensure_configuration():
        while True:
            time.sleep(30)
    logger.info("Starting Telegram bridge bot")
    offset = 0
    while True:
        try:
            updates = fetch_updates(offset)
            for update in updates:
                offset = max(offset, int(update.get("update_id", 0)) + 1)
                message = update.get("message")
                if message:
                    forward_user_message_to_chatservice(message)
            send_outbound_manager_replies()
        except Exception as exc:
            logger.exception("Telegram bridge loop error: %s", exc)
            time.sleep(3)
            continue

        time.sleep(IDLE_SLEEP)


if __name__ == "__main__":
    main()
