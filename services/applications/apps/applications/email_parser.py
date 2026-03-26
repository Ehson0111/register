import imaplib
import email
import re
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from html import unescape

from django.utils import timezone

from .models import Applications


def decode_mime_header(value: str) -> str:
    """Полная декодировка Subject/From с несколькими MIME-чанками."""
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
    """Грубое преобразование HTML в текст без внешних зависимостей."""
    if not html:
        return ""
    html = re.sub(
        r"<(script|style)[^>]*>.*?</\1>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</div\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</tr\s*>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", html)
    text = unescape(text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def refine_subject(raw_subject: str, body: str) -> str:
    """
    Если в Subject шаблон Яндекс.Форм («Например: …»), берём название из тела.
    """
    subject = decode_mime_header(raw_subject) if raw_subject else ""
    subject = subject.strip().strip("\t")
    body = body or ""

    placeholder = bool(
        re.search(r"Например", subject, re.I)
        or (subject.startswith('"') and "Новая заявка" in subject and "сайта" in subject)
    )

    if not placeholder and subject:
        return subject

    m = re.search(r"Название сделки:\s*(.+)", body, re.MULTILINE | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    m = re.search(r"^Новая заявка:\s*(.+)$", body, re.MULTILINE)
    if m:
        return f"Новая заявка: {m.group(1).strip()}"

    for line in body.splitlines():
        line = line.strip()
        if line and len(line) < 300 and not line.startswith("КОМУ"):
            return line

    return subject or "Заявка с формы"


class YandexMailParser:
    def __init__(self, email_address, password, *, imap_host="imap.yandex.ru", target_sender=None):
        self.email_address = email_address
        self.password = password
        self.imap_host = imap_host
        self.target_sender = target_sender or "69aeaa09eb6146cd4fd99c6b@forms.yandex.com"
        self.imap = None

    def connect(self):
        """Подключение к почте"""
        self.imap = imaplib.IMAP4_SSL(self.imap_host)
        self.imap.login(self.email_address, self.password)
        self.imap.select("inbox")

    def disconnect(self):
        """Отключение от почты"""
        if self.imap:
            try:
                self.imap.close()
            except Exception:
                pass
            try:
                self.imap.logout()
            except Exception:
                pass

    def get_text_from_msg(self, msg):
        """Текст письма: сначала text/plain, иначе text/html."""
        plain_parts = []
        html_parts = []

        def collect_from_part(part):
            ctype = part.get_content_type()
            if ctype not in ("text/plain", "text/html"):
                return
            try:
                payload = part.get_payload(decode=True)
            except Exception:
                return
            if not payload:
                return
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="ignore")
            except Exception:
                decoded = payload.decode("utf-8", errors="ignore")
            if ctype == "text/plain":
                plain_parts.append(decoded)
            else:
                html_parts.append(decoded)

        if msg.is_multipart():
            for part in msg.walk():
                collect_from_part(part)
        else:
            ctype = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True)
            except Exception:
                payload = None
            if not payload:
                return ""
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="ignore")
            except Exception:
                decoded = payload.decode("utf-8", errors="ignore")
            if ctype == "text/html":
                html_parts.append(decoded)
            else:
                plain_parts.append(decoded)

        if plain_parts:
            return "\n\n".join(plain_parts).strip()
        if html_parts:
            return html_to_text("\n".join(html_parts))
        return ""

    def _sender_from_message(self, msg) -> str:
        from_header = msg.get("From", "")
        if not from_header:
            return self.target_sender
        _, addr = parseaddr(decode_mime_header(from_header))
        return addr or self.target_sender

    def parse_and_save(self):
        """Парсинг писем и сохранение в БД"""
        try:
            if not self.email_address or not self.password:
                return {"error": "Не заданы YANDEX_EMAIL / YANDEX_PASSWORD"}

            self.connect()

            status, ids = self.imap.search(None, f'FROM "{self.target_sender}"')
            msg_ids = ids[0].split()

            new_applications = 0
            duplicates = 0

            for msg_id in msg_ids:
                status, data = self.imap.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
                message_id_header = data[0][1].decode("utf-8", errors="ignore")

                message_id_match = re.search(r"Message-ID:\s*<([^>]+)>", message_id_header, re.I)
                message_id = message_id_match.group(1) if message_id_match else str(msg_id)

                if Applications.objects.filter(message_id=message_id).exists():
                    duplicates += 1
                    continue

                status, data = self.imap.fetch(msg_id, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                raw_subject = msg.get("Subject", "") or ""
                subject_decoded = decode_mime_header(raw_subject)

                date_str = msg.get("Date")
                try:
                    date = parsedate_to_datetime(date_str) if date_str else timezone.now()
                except Exception:
                    date = timezone.now()

                text = self.get_text_from_msg(msg)
                subject = refine_subject(raw_subject, text)
                if not subject and subject_decoded:
                    subject = subject_decoded

                sender_email = self._sender_from_message(msg)

                Applications.objects.create(
                    subject=subject,
                    date=date,
                    text=text,
                    sender_email=sender_email,
                    message_id=message_id,
                    is_processed=False,
                )
                new_applications += 1

                self.imap.store(msg_id, "+FLAGS", "\\Seen")

            return {
                "total": len(msg_ids),
                "new": new_applications,
                "duplicates": duplicates,
            }

        except Exception as e:
            return {"error": str(e)}
        finally:
            self.disconnect()
