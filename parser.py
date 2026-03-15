import imaplib
import email
from email.header import decode_header

EMAIL = "ehsonboboev7@yandex.ru"
PASSWORD = "hbewwdgiloviutid"
SENDER = "69aeaa09eb6146cd4fd99c6b@forms.yandex.com"

# Подключение
imap = imaplib.IMAP4_SSL("imap.yandex.ru")
imap.login(EMAIL, PASSWORD)
imap.select("inbox")

# Поиск писем от отправителя
status, ids = imap.search(None, f'FROM "{SENDER}"')
msg_ids = ids[0].split()

print(f"Писем от {SENDER}: {len(msg_ids)}")

# Чтение писем
for msg_id in msg_ids:
    status, data = imap.fetch(msg_id, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    
    # Тема
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()
    
    print(f"\nТема: {subject}")
    print(f"Дата: {msg.get('Date')}")
    
    # Текст
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                print(f"Текст: {body[:200]}...")
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        print(f"Текст: {body[:200]}...")

imap.close()
imap.logout()