import imaplib
import email
from email.header import decode_header
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from pathlib import Path
import re

class YandexMailParser:
    """Класс для парсинга писем из Яндекс.Почты"""
    
    def __init__(self, host: str, email_addr: str, password: str, target_sender: str = None):
        """
        Инициализация парсера
        
        Args:
            host: IMAP сервер
            email_addr: Email адрес
            password: Пароль
            target_sender: Отправитель для фильтрации (опционально)
        """
        self.host = host
        self.email = email_addr
        self.password = password
        self.target_sender = target_sender
        self.connection = None
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mail_parser.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Подключение к почтовому серверу
        
        Returns:
            bool: Успешность подключения
        """
        try:
            self.connection = imaplib.IMAP4_SSL(self.host)
            self.connection.login(self.email, self.password)
            self.logger.info(f"Успешное подключение к {self.host}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {str(e)}")
            return False
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                self.logger.info("Отключено от сервера")
            except:
                pass
    
    def select_folder(self, folder: str = "INBOX") -> int:
        """
        Выбор папки для работы
        
        Args:
            folder: Имя папки (INBOX, Sent, Drafts и т.д.)
            
        Returns:
            int: Количество писем в папке
        """
        try:
            status, messages = self.connection.select(folder, readonly=True)
            if status == 'OK':
                message_count = int(messages[0])
                self.logger.info(f"Выбрана папка {folder}. Писем: {message_count}")
                return message_count
            else:
                self.logger.error(f"Не удалось выбрать папку {folder}")
                return 0
        except Exception as e:
            self.logger.error(f"Ошибка выбора папки: {str(e)}")
            return 0
    
    def decode_subject(self, subject: str) -> str:
        """Декодирование темы письма"""
        try:
            decoded_parts = decode_header(subject)
            decoded_subject = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    try:
                        decoded_subject += part.decode(encoding or 'utf-8')
                    except:
                        decoded_subject += part.decode('utf-8', errors='ignore')
                else:
                    decoded_subject += part
            return decoded_subject
        except:
            return subject
    
    def decode_body(self, body: bytes) -> str:
        """Декодирование тела письма"""
        try:
            return body.decode('utf-8', errors='ignore')
        except:
            try:
                return body.decode('windows-1251', errors='ignore')
            except:
                return str(body)
    
    def parse_email(self, email_message) -> Dict:
        """
        Парсинг одного письма
        
        Args:
            email_message: Email сообщение
            
        Returns:
            Dict: Структурированные данные письма
        """
        try:
            # Получение основных заголовков
            subject = self.decode_subject(email_message.get('Subject', 'No Subject'))
            from_addr = email_message.get('From', 'Unknown')
            to_addr = email_message.get('To', 'Unknown')
            date = email_message.get('Date', 'Unknown')
            
            # Получение тела письма
            body = ""
            attachments = []
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Обработка вложений
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': filename,
                                'content_type': content_type,
                                'size': len(part.get_payload(decode=True))
                            })
                    
                    # Обработка текстовой части
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = self.decode_body(payload)
                                break
                        except:
                            continue
            else:
                # Простое письмо без multipart
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = self.decode_body(payload)
            
            return {
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'date': date,
                'body': body.strip(),
                'attachments': attachments,
                'has_attachments': len(attachments) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга письма: {str(e)}")
            return None
    
    def search_emails(self, 
                     since_date: str = None,
                     before_date: str = None,
                     sender: str = None,
                     subject: str = None,
                     limit: int = None) -> List[Dict]:
        """
        Поиск писем по критериям
        
        Args:
            since_date: Поиск с даты (формат: DD-MMM-YYYY)
            before_date: Поиск до даты
            sender: Поиск по отправителю
            subject: Поиск по теме
            limit: Максимальное количество писем
            
        Returns:
            List[Dict]: Список найденных писем
        """
        try:
            # Формирование критериев поиска
            search_criteria = []
            
            if since_date:
                search_criteria.append(f'SINCE "{since_date}"')
            if before_date:
                search_criteria.append(f'BEFORE "{before_date}"')
            if sender:
                search_criteria.append(f'FROM "{sender}"')
            if subject:
                search_criteria.append(f'SUBJECT "{subject}"')
            
            # Если нет критериев, ищем все письма
            search_query = ' '.join(search_criteria) if search_criteria else 'ALL'
            
            self.logger.info(f"Поиск писем по критерию: {search_query}")
            
            # Выполнение поиска
            status, message_ids = self.connection.search(None, search_query)
            
            if status != 'OK':
                self.logger.error("Ошибка поиска писем")
                return []
            
            # Получение ID писем
            ids = message_ids[0].split()
            
            if not ids:
                self.logger.info("Письма не найдены")
                return []
            
            # Применение лимита
            if limit and limit < len(ids):
                ids = ids[:limit]
            
            self.logger.info(f"Найдено писем: {len(ids)}")
            
            # Парсинг писем
            emails_data = []
            for msg_id in ids:
                try:
                    # Получение письма
                    status, msg_data = self.connection.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Парсинг письма
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Проверка отправителя если указан
                    from_addr = email_message.get('From', '')
                    if self.target_sender and self.target_sender not in from_addr:
                        continue
                    
                    # Парсинг письма
                    parsed_email = self.parse_email(email_message)
                    if parsed_email:
                        parsed_email['id'] = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)
                        emails_data.append(parsed_email)
                        
                except Exception as e:
                    self.logger.error(f"Ошибка обработки письма {msg_id}: {str(e)}")
                    continue
            
            return emails_data
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска: {str(e)}")
            return []
    
    def get_emails_from_sender(self, days_back: int = 7, limit: int = None) -> List[Dict]:
        """
        Получение писем от определенного отправителя
        
        Args:
            days_back: Количество дней назад
            limit: Максимальное количество писем
            
        Returns:
            List[Dict]: Список писем
        """
        if not self.target_sender:
            self.logger.error("Не указан отправитель для фильтрации")
            return []
        
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        return self.search_emails(sender=self.target_sender, since_date=since_date, limit=limit)
    
    def save_emails_to_json(self, emails: List[Dict], filename: str = "emails.json"):
        """Сохранение писем в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(emails, f, ensure_ascii=False, indent=2, default=str)
            self.logger.info(f"Сохранено {len(emails)} писем в {filename}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения: {str(e)}")
    
    def save_emails_to_files(self, emails: List[Dict], output_dir: str = "emails"):
        """Сохранение каждого письма в отдельный файл"""
        try:
            # Создание директории
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for idx, email_data in enumerate(emails, 1):
                # Очистка имени файла от недопустимых символов
                subject = re.sub(r'[\\/*?:"<>|]', "_", email_data['subject'][:50])
                filename = f"{output_dir}/email_{idx}_{subject}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"От: {email_data['from']}\n")
                    f.write(f"Кому: {email_data['to']}\n")
                    f.write(f"Дата: {email_data['date']}\n")
                    f.write(f"Тема: {email_data['subject']}\n")
                    f.write("-" * 50 + "\n")
                    f.write(email_data['body'])
                    
                    if email_data['attachments']:
                        f.write("\n\n" + "-" * 50 + "\n")
                        f.write("Вложения:\n")
                        for att in email_data['attachments']:
                            f.write(f"- {att['filename']} ({att['size']} bytes)\n")
                
                self.logger.info(f"Сохранено: {filename}")
                
        except Exception as e:
            self.logger.error(f"Ошибка сохранения: {str(e)}")
    
    def extract_links_from_emails(self, emails: List[Dict]) -> List[str]:
        """
        Извлечение ссылок из писем
        
        Args:
            emails: Список писем
            
        Returns:
            List[str]: Список найденных ссылок
        """
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[^\s]*)?'
        all_links = []
        
        for email_data in emails:
            links = re.findall(url_pattern, email_data['body'])
            all_links.extend(links)
        
        return list(set(all_links))  # Удаление дубликатов


def main():
    """Основная функция для запуска парсера"""
    
    # Конфигурация (можно загрузить из .env файла)
    config = {
        'YANDEX_IMAP_HOST': 'imap.yandex.ru',
        'YANDEX_EMAIL': 'ehsonboboev7@yandex.ru',
        'YANDEX_PASSWORD': 'hbewwdgiloviutid',
        'YANDEX_TARGET_SENDER': '69aeaa09eb6146cd4fd99c6b@forms.yandex.com'
    }
    
    # Создание парсера
    parser = YandexMailParser(
        host=config['YANDEX_IMAP_HOST'],
        email_addr=config['YANDEX_EMAIL'],
        password=config['YANDEX_PASSWORD'],
        target_sender=config['YANDEX_TARGET_SENDER']
    )
    
    try:
        # Подключение
        if not parser.connect():
            return
        
        # Выбор папки Входящие
        parser.select_folder("INBOX")
        
        # Получение писем от конкретного отправителя за последние 30 дней
        emails = parser.get_emails_from_sender(days_back=30)
        
        if emails:
            print(f"\nНайдено писем: {len(emails)}")
            
            # Вывод информации о найденных письмах
            for i, email_data in enumerate(emails, 1):
                print(f"\nПисьмо {i}:")
                print(f"  Тема: {email_data['subject']}")
                print(f"  От: {email_data['from']}")
                print(f"  Дата: {email_data['date']}")
                print(f"  Длина текста: {len(email_data['body'])} символов")
                if email_data['has_attachments']:
                    print(f"  Вложения: {len(email_data['attachments'])}")
            
            # Сохранение в JSON
            parser.save_emails_to_json(emails, "yandex_emails.json")
            
            # Сохранение в отдельные файлы
            parser.save_emails_to_files(emails, "yandex_emails")
            
            # Извлечение ссылок
            links = parser.extract_links_from_emails(emails)
            if links:
                print(f"\nНайдено ссылок: {len(links)}")
                for link in links:
                    print(f"  {link}")
                
                # Сохранение ссылок
                with open('extracted_links.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(links))
        else:
            print("Письма не найдены")
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")
    finally:
        # Отключение
        parser.disconnect()


if __name__ == "__main__":
    main()