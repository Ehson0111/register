"""Подстановка {переменных} в шаблоны писем."""

import re

from django.utils import timezone

_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")
_HTML_HINT_RE = re.compile(r"<html>|<p>|<br>", re.I)


def build_recipient_variables(
    client_info,
    common_variables,
    recipient_id,
    manager_id,
    campaign_name,
) -> dict:
    variables = {}
    if client_info:
        name = client_info.get("name") or client_info.get("client_name", "")
        variables.update(
            {
                "client_id": client_info.get("id", recipient_id),
                "client_name": name,
                "name": name,
                "client_email": client_info.get("email", ""),
                "phone": client_info.get("phone", ""),
                "company": client_info.get("company", ""),
            }
        )
    variables.update(common_variables or {})
    variables.update(
        {
            "manager_id": manager_id,
            "date": timezone.now().strftime("%d.%m.%Y"),
            "campaign_name": campaign_name,
        }
    )
    return variables


def render_placeholders(text, variables: dict) -> str:
    def replace(match):
        key = match.group(1)
        if key in variables:
            return str(variables[key])
        if key in ("name", "client_name"):
            return "Уважаемый клиент"
        return f"[{key}]"

    return _PLACEHOLDER_RE.sub(replace, text or "")


def content_is_html(content: str) -> bool:
    return bool(_HTML_HINT_RE.search(content or ""))
