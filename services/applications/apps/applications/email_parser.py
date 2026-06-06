import imaplib
import re
from email import message_from_bytes

from .mail_utils import (
    decode_mime_header,
    normalize_message_id,
    parse_message_date,
    refine_subject,
    sender_from_message,
    message_plain_text,
)
from .models import Applications


class YandexMailParser:
    def __init__(self, email_address, password, *, imap_host="imap.yandex.ru", target_sender=None):
        self.email_address = email_address
        self.password = password
        self.imap_host = imap_host
        self.target_sender = target_sender or "69aeaa09eb6146cd4fd99c6b@forms.yandex.com"
        self.imap = None

    def connect(self):
        self.imap = imaplib.IMAP4_SSL(self.imap_host)
        self.imap.login(self.email_address, self.password)
        self.imap.select("inbox")

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

    def parse_and_save(self):
        try:
            if not self.email_address or not self.password:
                return {"error": "Не заданы YANDEX_EMAIL / YANDEX_PASSWORD"}

            self.connect()

            status, ids = self.imap.search(None, f'FROM "{self.target_sender}"')
            msg_ids = ids[0].split() # список target_sender Возвращает список ID писем: [b'1', b'2', b'3']



            new_applications = 0
            duplicates = 0

            for msg_id in msg_ids:
                status, data = self.imap.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
                message_id_header = data[0][1].decode("utf-8", errors="ignore")
                message_id_match = re.search(r"Message-ID:\s*<([^>]+)>", message_id_header, re.I)
                message_id = normalize_message_id(
                    message_id_match.group(1) if message_id_match else None,
                    str(msg_id),
                )
                  
                existing = Applications.objects.filter(message_id=message_id).first()
                if existing:
                    duplicates += 1
                    # Обновляем текст, если в почте появился более полный вариант (старые импорты без HTML-полей)
                    status, data = self.imap.fetch(msg_id, "(RFC822)")
                    email_msg = message_from_bytes(data[0][1])
                    fresh_text = message_plain_text(email_msg)
                    if len(fresh_text) > len(existing.text or "") + 20:
                        raw_subject = email_msg.get("Subject", "") or ""
                        existing.text = fresh_text
                        existing.subject = refine_subject(raw_subject, fresh_text) or existing.subject
                        existing.save(update_fields=["text", "subject", "updated_at"])
                    continue

                status, data = self.imap.fetch(msg_id, "(RFC822)")
                email_msg = message_from_bytes(data[0][1])

                raw_subject = email_msg.get("Subject", "") or ""
                subject_decoded = decode_mime_header(raw_subject)
                date = parse_message_date(email_msg.get("Date"))
                text = message_plain_text(email_msg)
                subject = refine_subject(raw_subject, text)
                if not subject and subject_decoded:
                    subject = subject_decoded

                sender_email = sender_from_message(email_msg, self.target_sender)

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

        except Exception as exc:
            return {"error": str(exc)}
        finally:
            self.disconnect()
