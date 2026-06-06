"""Общие утилиты для разбора писем (IMAP/Yandex)."""
import re
from email.header import decode_header
from email.utils import getaddresses, parseaddr, parsedate_to_datetime

import html2text
import mailparser
from django.utils import timezone

_HTML_CONVERTER = html2text.HTML2Text()
_HTML_CONVERTER.ignore_links = False
_HTML_CONVERTER.ignore_images = True
_HTML_CONVERTER.body_width = 0


def decode_mime_header(value: str) -> str:
    if not value:
        return ""
    parts = []
    for chunk, charset in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts).strip()


def html_to_text(html: str) -> str:
    if not html:
        return ""
    return _HTML_CONVERTER.handle(html).strip()


def parse_raw_email(raw_bytes: bytes) -> mailparser.MailParser:
    return mailparser.parse_from_bytes(raw_bytes)


def parse_message(msg) -> mailparser.MailParser:
    return mailparser.parse_from_bytes(msg.as_bytes())


def mailparser_text(value) -> str:
    """mail-parser 4.x отдаёт text_plain/text_html списком строк."""
    if not value:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n\n".join(str(part).strip() for part in value if part).strip()
    return str(value).strip()


def message_bodies(msg) -> tuple[str, str]:
    """Возвращает (text/plain, text/html)."""
    parsed = parse_message(msg)
    plain = mailparser_text(parsed.text_plain)
    html = mailparser_text(parsed.text_html)
    if not plain and html:
        plain = html_to_text(html)
    if not plain:
        plain = mailparser_text(getattr(parsed, "body", ""))
    return plain, html


def message_plain_text(msg) -> str:
    plain, html = message_bodies(msg)
    html_as_text = html_to_text(html) if html else ""
    # У Яндекс.Форм полный текст часто только в HTML — берём более полный вариант.
    if len(html_as_text) > len(plain) + 20:
        return html_as_text
    return plain or html_as_text


def addresses_to_string(raw: str) -> str:
    addresses = [addr for _, addr in getaddresses([raw or ""]) if addr]
    return ", ".join(addresses)


def preview_text(text: str, limit: int = 180) -> str:
    compact = " ".join((text or "").split())
    return compact[:limit].strip()


def refine_subject(raw_subject: str, body: str) -> str:
    """Если Subject — шаблон Яндекс.Форм, берём название из тела."""
    subject = decode_mime_header(raw_subject) if raw_subject else ""
    subject = subject.strip().strip("\t")
    body = body or ""

    placeholder = bool(
        re.search(r"Например", subject, re.I)
        or (subject.startswith('"') and "Новая заявка" in subject and "сайта" in subject)
    )

    if not placeholder and subject:
        return subject

    match = re.search(r"Название сделки:\s*(.+)", body, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"^Новая заявка:\s*(.+)$", body, re.MULTILINE)
    if match:
        return f"Новая заявка: {match.group(1).strip()}"

    for line in body.splitlines():
        line = line.strip()
        if line and len(line) < 300 and not line.startswith("КОМУ"):
            return line

    return subject or "Заявка с формы"


def normalize_message_id(value: str | None, fallback: str) -> str:
    message_id = (value or "").strip().strip("<>").strip()
    return message_id or fallback


def parse_message_date(date_header: str | None):
    try:
        if date_header:
            parsed = parsedate_to_datetime(date_header)
            if timezone.is_naive(parsed):
                return timezone.make_aware(parsed, timezone.get_current_timezone())
            return parsed
    except Exception:
        pass
    return timezone.now()


def sender_email_from_parsed(parsed: mailparser.MailParser, fallback: str) -> str:
    if parsed.from_:
        for _name, addr in parsed.from_:
            if addr:
                return addr
    return fallback


def sender_from_message(msg, fallback: str) -> str:
    from_header = msg.get("From", "")
    if not from_header:
        return fallback
    _, addr = parseaddr(decode_mime_header(from_header))
    return addr or fallback


def flags_from_fetch_meta(meta: str) -> list[str]:
    flags_match = re.search(r"FLAGS \((.*?)\)", meta or "")
    if not flags_match:
        return []
    return [flag.strip() for flag in flags_match.group(1).split() if flag.strip()]
