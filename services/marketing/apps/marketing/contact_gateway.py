"""Запросы к contact-service через API gateway (с тем же JWT, что у менеджера)."""

import logging
import os

import requests

logger = logging.getLogger(__name__)

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
FORWARD_HEADERS = (
    "Authorization",
    "Content-Type",
    "Accept",
    "User-Agent",
    "Accept-Language",
    "Accept-Encoding",
)


def _proxy_headers(request) -> dict:
    return {h: request.headers[h] for h in FORWARD_HEADERS if request.headers.get(h)}


def _fallback_contact(client_id: int) -> dict:
    return {
        "id": client_id,
        "name": f"Клиент #{client_id}",
        "email": f"client{client_id}@example.com",
        "phone": "+7999000" + str(client_id).zfill(4),
    }


def fetch_contact(request, client_id: int) -> dict:
    """Один контакт: GET /api/contacts/{id}/ через gateway."""
    try:
        response = requests.get(
            f"{GATEWAY_URL}/api/contacts/{client_id}/",
            headers=_proxy_headers(request),
            params=dict(request.GET.items()),
            timeout=30,
        )
        if response.status_code in (200, 201):
            return response.json()
        logger.error("Contact %s: HTTP %s", client_id, response.status_code)
    except requests.RequestException as exc:
        logger.error("Contact %s: %s", client_id, exc)
    return _fallback_contact(client_id)


def fetch_contacts_map(request, client_ids: list) -> dict:
    """Словарь {contact_id: данные} для списка получателей рассылки."""
    return {cid: fetch_contact(request, cid) for cid in client_ids}
