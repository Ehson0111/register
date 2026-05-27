"""
Telegram ↔ chat-service мост на python-telegram-bot (long polling).

Поток:
  1) клиент пишет боту → POST /api/chat/telegram/inbound/
  2) менеджер отвечает в CRM → периодический poll outbound → sendMessage в Telegram
"""

import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bridge_client import ChatServiceBridge
from config import (
    BOT_TOKEN,
    BRIDGE_SECRET,
    CHAT_SERVICE_URL,
    LOG_LEVEL,
    OUTBOUND_LIMIT,
    POLL_INTERVAL,
    WELCOME_TEXT,
)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("tg-bridge-bot")

bridge = ChatServiceBridge(CHAT_SERVICE_URL, BRIDGE_SECRET)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие по /start (в CRM не уходит)."""
    if update.effective_chat:
        await update.effective_chat.send_message(WELCOME_TEXT[:4000])


async def on_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Текст из лички → chat-service."""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if chat.type != "private":
        return

    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return

    await bridge.forward_inbound(
        {
            "chat_id": chat.id,
            "text": text,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
        }
    )


async def deliver_manager_replies(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Периодически забираем ответы менеджеров и шлём в Telegram."""
    items = await bridge.fetch_outbound(limit=OUTBOUND_LIMIT)
    for item in items:
        chat_id = item.get("chat_id")
        text = item.get("text", "")
        sender_name = item.get("sender_name", "Менеджер")
        if chat_id is None:
            continue
        formatted = f"{sender_name}:\n{text}"[:4000]
        try:
            await context.bot.send_message(chat_id=chat_id, text=formatted)
            logger.info(
                "Outbound sent: chat_id=%s message_id=%s",
                chat_id,
                item.get("message_id"),
            )
        except Exception:
            logger.exception("Failed to send outbound to chat_id=%s", chat_id)


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not BRIDGE_SECRET:
        raise RuntimeError("TELEGRAM_BRIDGE_SECRET is not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(
        MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, on_private_text)
    )
    app.job_queue.run_repeating(
        deliver_manager_replies,
        interval=POLL_INTERVAL,
        first=POLL_INTERVAL,
        name="outbound-poll",
    )
    return app


def main() -> None:
    try:
        application = build_application()
    except RuntimeError as exc:
        logger.warning("%s — bot idle", exc)
        import time

        while True:
            time.sleep(30)
        return

    logger.info("Starting Telegram bridge (PTB polling)")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
