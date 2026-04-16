import email
import hashlib
import imaplib
import re
import smtplib
from email.header import decode_header
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr, parsedate_to_datetime
from html import unescape

from django.utils import timezone

from .models import MailboxEmail


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
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</div\s*>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", html)
    text = unescape(text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def addresses_to_string(raw: str) -> str:
    addresses = [addr for _, addr in getaddresses([raw or ""]) if addr]
    return ", ".join(addresses)


def preview_text(text: str, limit: int = 180) -> str:
    compact = " ".join((text or "").split())
    return compact[:limit].strip()


class YandexMailboxClient:
    def __init__(
        self,
        email_address,
        password,
        *,
        imap_host="imap.yandex.ru",
        smtp_host="smtp.yandex.ru",
        smtp_port=465,
        smtp_use_ssl=True,
    ):
        self.email_address = email_address
        self.password = password
        self.imap_host = imap_host
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_use_ssl = smtp_use_ssl
        self.imap = None

    def connect(self):
        self.imap = imaplib.IMAP4_SSL(self.imap_host)
        self.imap.login(self.email_address, self.password)

    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
            except Exception:
                pass
            try:
                self.imap.logout()
            except Exception:
                pass

    def _select_mailbox(self, mailbox_name: str) -> bool:
        candidates = [mailbox_name]
        if mailbox_name.upper() != "INBOX":
            candidates.append(f'"{mailbox_name}"')
        for candidate in candidates:
            try:
                status, _ = self.imap.select(candidate)
                if status == "OK":
                    return True
            except Exception:
                continue
        return False

    def _resolve_folder(self, folder_kind: str):
        variants = {
            MailboxEmail.FOLDER_INBOX: ["INBOX"],
            MailboxEmail.FOLDER_SENT: ["Sent", "Sent Messages", "Отправленные"],
            MailboxEmail.FOLDER_TRASH: ["Trash", "Deleted Messages", "Удаленные", "Deleted"],
        }
        for candidate in variants.get(folder_kind, []):
            if self._select_mailbox(candidate):
                return candidate
        return None

    def _extract_bodies(self, msg):
        plain_parts = []
        html_parts = []

        def collect(part):
            content_type = part.get_content_type()
            disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disposition:
                return
            if content_type not in ("text/plain", "text/html"):
                return
            payload = part.get_payload(decode=True)
            if not payload:
                return
            charset = part.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, errors="replace")
            except Exception:
                text = payload.decode("utf-8", errors="replace")
            if content_type == "text/plain":
                plain_parts.append(text)
            else:
                html_parts.append(text)

        if msg.is_multipart():
            for part in msg.walk():
                collect(part)
        else:
            collect(msg)

        body_text = "\n\n".join(part.strip() for part in plain_parts if part.strip()).strip()
        body_html = "\n".join(part for part in html_parts if part).strip()
        if not body_text and body_html:
            body_text = html_to_text(body_html)
        return body_text, body_html

    def _external_id(self, msg, msg_id, folder_kind):
        message_id = (msg.get("Message-ID") or "").strip().strip("<>").strip()
        if message_id:
            return message_id
        fingerprint = "|".join(
            [
                folder_kind,
                decode_mime_header(msg.get("Subject", "")),
                msg.get("Date", ""),
                parseaddr(msg.get("From", ""))[1],
                addresses_to_string(msg.get("To", "")),
                str(msg_id),
            ]
        )
        return hashlib.sha1(fingerprint.encode("utf-8", errors="ignore")).hexdigest()

    def _message_record(self, msg, flags, folder_kind, msg_id):
        body_text, body_html = self._extract_bodies(msg)
        subject = decode_mime_header(msg.get("Subject", "")) or "Без темы"
        from_name, from_email = parseaddr(decode_mime_header(msg.get("From", "")))

        try:
            message_date = parsedate_to_datetime(msg.get("Date")) if msg.get("Date") else timezone.now()
            if timezone.is_naive(message_date):
                message_date = timezone.make_aware(message_date, timezone.get_current_timezone())
        except Exception:
            message_date = timezone.now()

        normalized_flags = [flag.strip() for flag in flags if flag.strip()]
        important = "\\Flagged" in normalized_flags or (msg.get("Importance", "").lower() == "high")
        external_id = self._external_id(msg, msg_id, folder_kind)

        return {
            "external_id": external_id,
            "message_id": (msg.get("Message-ID") or "").strip().strip("<>").strip(),
            "subject": subject,
            "sender_name": decode_mime_header(from_name),
            "sender_email": from_email,
            "recipients": addresses_to_string(msg.get("To", "")),
            "cc": addresses_to_string(msg.get("Cc", "")),
            "date": message_date,
            "body_text": body_text,
            "body_html": body_html,
            "preview": preview_text(body_text or body_html),
            "is_read": "\\Seen" in normalized_flags,
            "is_important": important,
            "raw_flags": normalized_flags,
            "in_inbox": folder_kind == MailboxEmail.FOLDER_INBOX,
            "in_sent": folder_kind == MailboxEmail.FOLDER_SENT,
            "in_trash": folder_kind == MailboxEmail.FOLDER_TRASH,
            "primary_folder": folder_kind,
        }

    def sync_mailbox(self):
        if not self.email_address or not self.password:
            return {"error": "Не заданы почтовые логин/пароль"}

        try:
            self.connect()
            collected = {}
            folder_stats = {}

            for folder_kind in [MailboxEmail.FOLDER_INBOX, MailboxEmail.FOLDER_SENT, MailboxEmail.FOLDER_TRASH]:
                mailbox_name = self._resolve_folder(folder_kind)
                if not mailbox_name:
                    folder_stats[folder_kind] = {"mailbox": None, "loaded": 0}
                    continue

                status, ids = self.imap.search(None, "ALL")
                msg_ids = ids[0].split() if status == "OK" and ids and ids[0] else []
                folder_stats[folder_kind] = {"mailbox": mailbox_name, "loaded": len(msg_ids)}

                for msg_id in msg_ids:
                    status, data = self.imap.fetch(msg_id, "(RFC822 FLAGS)")
                    if status != "OK":
                        continue

                    raw_bytes = None
                    meta = ""
                    for item in data:
                        if isinstance(item, tuple):
                            meta = item[0].decode("utf-8", errors="ignore")
                            raw_bytes = item[1]
                            break
                    if not raw_bytes:
                        continue

                    flags_match = re.search(r"FLAGS \((.*?)\)", meta)
                    flags = flags_match.group(1).split() if flags_match else []
                    msg = email.message_from_bytes(raw_bytes)
                    record = self._message_record(msg, flags, folder_kind, msg_id)
                    existing = collected.get(record["external_id"])
                    if existing:
                        existing["in_inbox"] = existing["in_inbox"] or record["in_inbox"]
                        existing["in_sent"] = existing["in_sent"] or record["in_sent"]
                        existing["in_trash"] = existing["in_trash"] or record["in_trash"]
                        existing["is_important"] = existing["is_important"] or record["is_important"]
                        existing["is_read"] = existing["is_read"] or record["is_read"]
                        existing["raw_flags"] = sorted(set(existing["raw_flags"] + record["raw_flags"]))
                        if existing["primary_folder"] == MailboxEmail.FOLDER_INBOX and record["in_sent"]:
                            existing["primary_folder"] = MailboxEmail.FOLDER_SENT
                        if record["in_trash"]:
                            existing["primary_folder"] = MailboxEmail.FOLDER_TRASH
                    else:
                        collected[record["external_id"]] = record

            created = 0
            updated = 0
            for external_id, payload in collected.items():
                _, was_created = MailboxEmail.objects.update_or_create(
                    external_id=external_id,
                    defaults=payload,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            return {
                "synced": len(collected),
                "created": created,
                "updated": updated,
                "folders": folder_stats,
            }
        except Exception as exc:
            return {"error": str(exc)}
        finally:
            self.disconnect()

    def send_email(self, *, to, subject, body, cc=""):
        if not self.email_address or not self.password:
            raise ValueError("Не заданы почтовые логин/пароль")

        msg = EmailMessage()
        msg["From"] = self.email_address
        msg["To"] = to
        if cc:
            msg["Cc"] = cc
        msg["Subject"] = subject or "Без темы"
        msg.set_content(body or "")

        recipients = [addr for _, addr in getaddresses([to, cc]) if addr]
        if self.smtp_use_ssl:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as smtp:
                smtp.login(self.email_address, self.password)
                smtp.send_message(msg, from_addr=self.email_address, to_addrs=recipients)
        else:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(self.email_address, self.password)
                smtp.send_message(msg, from_addr=self.email_address, to_addrs=recipients)

        return {
            "subject": msg["Subject"],
            "recipients": to,
            "cc": cc,
            "body_text": body or "",
        }
