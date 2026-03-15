import imaplib
import email
from email.header import decode_header
from django.utils import timezone
from .models import Applications

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
            self.imap.close()
            self.imap.logout()
    
    def get_text_from_msg(self, msg):
        """Извлечение текста из письма"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""
    
    def parse_and_save(self):
        """Парсинг писем и сохранение в БД"""
        try:
            if not self.email_address or not self.password:
                return {'error': 'Не заданы YANDEX_EMAIL / YANDEX_PASSWORD'}

            self.connect()
            
            # Поиск писем только от нужного отправителя
            status, ids = self.imap.search(None, f'FROM "{self.target_sender}"')
            msg_ids = ids[0].split()
            
            new_applications = 0
            duplicates = 0
            
            for msg_id in msg_ids:
                # Получаем Message-ID письма для проверки дубликатов
                status, data = self.imap.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])')
                message_id_header = data[0][1].decode('utf-8', errors='ignore')
                
                # Парсим Message-ID
                import re
                message_id_match = re.search(r'Message-ID: <(.*)>', message_id_header)
                message_id = message_id_match.group(1) if message_id_match else str(msg_id)
                
                # Проверяем, есть ли уже такое письмо
                if Applications.objects.filter(message_id=message_id).exists():
                    duplicates += 1
                    continue
                
                # Получаем полное письмо
                status, data = self.imap.fetch(msg_id, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                
                # Декодируем тему
                subject = decode_header(msg.get("Subject", ""))[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode('utf-8', errors='ignore') or ''
                
                # Дата письма
                date_str = msg.get("Date")
                # Преобразуем дату из формата письма в datetime
                from email.utils import parsedate_to_datetime
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    date = timezone.now()
                
                # Текст письма
                text = self.get_text_from_msg(msg)
                
                # Создаем заявку
                Applications.objects.create(
                    subject=subject,
                    date=date,
                    text=text,
                    sender_email=self.target_sender,
                    message_id=message_id,
                    is_processed=False
                )
                new_applications += 1
                
                # Помечаем письмо как прочитанное (опционально)
                self.imap.store(msg_id, '+FLAGS', '\\Seen')
            
            return {
                'total': len(msg_ids),
                'new': new_applications,
                'duplicates': duplicates
            }
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            self.disconnect()