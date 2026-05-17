import hashlib
import imaplib
import smtplib
from email import message_from_bytes
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr

from .mail_utils import (
    addresses_to_string,
    decode_mime_header,
    flags_from_fetch_meta,
    message_bodies,
    parse_message_date,
    preview_text,
)
from .models import MailboxEmail


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
        body_text, body_html = message_bodies(msg)
        subject = decode_mime_header(msg.get("Subject", "")) or "Без темы"
        from_name, from_email = parseaddr(decode_mime_header(msg.get("From", "")))
        message_date = parse_message_date(msg.get("Date"))

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

                    flags = flags_from_fetch_meta(meta)
                    msg = message_from_bytes(raw_bytes)
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
