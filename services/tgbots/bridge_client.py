"""HTTP-клиент к chat-service (inbound/outbound мост)."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ChatServiceBridge:
    def __init__(self, base_url: str, secret: str):
        self._inbound_url = f"{base_url}/api/chat/telegram/inbound/"
        self._outbound_url = f"{base_url}/api/chat/telegram/outbound/"
        self._headers = {
            "X-Telegram-Bridge-Secret": secret,
            "Content-Type": "application/json",
        }

    async def forward_inbound(self, payload: dict[str, Any]) -> bool:
        """Сообщение клиента из Telegram → chat-service."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._inbound_url, json=payload, headers=self._headers
                )
            if response.status_code >= 300:
                logger.error(
                    "Inbound failed: %s %s", response.status_code, response.text
                )
                return False
            logger.info("Inbound delivered: chat_id=%s", payload.get("chat_id"))
            return True
        except httpx.HTTPError as exc:
            logger.exception("Inbound request error: %s", exc)
            return False

    async def fetch_outbound(self, limit: int = 100) -> list[dict[str, Any]]:
        """Ответы менеджера из CRM, ещё не отправленные в Telegram."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self._outbound_url,
                    params={"limit": limit},
                    headers=self._headers,
                )
            if response.status_code >= 300:
                logger.error(
                    "Outbound poll failed: %s %s", response.status_code, response.text
                )
                return []
            return (response.json() or {}).get("messages", [])
        except httpx.HTTPError as exc:
            logger.exception("Outbound poll error: %s", exc)
            return []
