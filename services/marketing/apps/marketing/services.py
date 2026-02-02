# import smtplib
# import logging
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from django.conf import settings
# from django.utils import timezone

# logger = logging.getLogger(__name__)


# class EmailService:
#     """Сервис для отправки email через Yandex"""
    
#     def __init__(self):
#         # Конфигурация Yandex SMTP
#         self.smtp_server = 'smtp.yandex.ru'
#         self.smtp_port = 465
#         self.smtp_username = 'ehsonboboev7@yandex.ru'
#         self.smtp_password = 'hbewwdgiloviutid'  # В продакшене используйте переменные окружения
        
   

     
#     def send_email(self, to_email, subject, content, from_email=None, is_html=False):
#         """
#         Отправка email

#         Args:
#             to_email: Email получателя
#             subject: Тема письма
#             content: Содержание письма
#             from_email: Email отправителя (если None, используется smtp_username)
#             is_html: Если True, контент отправляется как HTML

#         Returns:
#             bool: True если отправка успешна, False если ошибка
#         """
#         try:
#             # Создаем правильное сообщение в зависимости от типа
#             if is_html:
#                 msg = MIMEMultipart('alternative')
#                 # HTML часть
#                 html_part = MIMEText(content, 'html', 'utf-8')
#                 msg.attach(html_part)
#                 # Текстовая часть как fallback
#                 text_content = content
#                 # Простая попытка убрать HTML теги для текстовой версии
#                 import re
#                 text_content = re.sub('<[^<]+?>', '', text_content)
#                 text_part = MIMEText(text_content, 'plain', 'utf-8')
#                 msg.attach(text_part)
#             else:
#                 msg = MIMEText(content, 'plain', 'utf-8')

#             # Устанавливаем заголовки
#             msg['Subject'] = subject
#             msg['From'] = from_email if from_email else self.smtp_username
#             msg['To'] = to_email

#             # Дополнительные заголовки для предотвращения спама
#             msg['X-Mailer'] = 'Django Mail Service'
#             msg['X-Priority'] = '3'
#             msg['X-MSMail-Priority'] = 'Normal'

#             # Подключаемся к серверу и отправляем
#             server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
#             server.login(self.smtp_username, self.smtp_password)

#             # Отправляем с обработкой возможных ошибок
#             server.sendmail(
#                 msg['From'],
#                 [to_email],  # Список получателей
#                 msg.as_string()
#             )
#             server.quit()

#             logger.info(f"Email успешно отправлен: {to_email}, тема: {subject}")
#             return True

#         except smtplib.SMTPException as e:
#             logger.error(f"SMTP ошибка при отправке email на {to_email}: {str(e)}")
#             return False
#         except Exception as e:
#             logger.error(f"Общая ошибка при отправке email на {to_email}: {str(e)}")
#             return False     
#                         # import smtplib
#                         # from email.mime.text import MIMEText
                    
#                     # def quick_send_yandex():
#                     #     msg = MIMEText("Текст 1", 'plain', 'utf-8')
#                     #     msg['Subject'] = 'тестирование     '
#                     #     msg['From'] = 'ehsonboboev7@yandex.ru'
#                     #     msg['To'] = 'ehsonboboev7@gmail.com'
                        
#                     #     server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
#                     #     server.login('ehsonboboev7@yandex.ru', 'hbewwdgiloviutid')
#                     #     server.send_message(msg)
#                     #     server.quit()
#                     #     print("Письмо отправлено!")
                    
#                     # quick_send_yandex()

#     # почта to_email — email получателя (например: ivan@example.com)
#           # template — объект шаблона с полями:
#           # template.subject — тема письма
#           # template.content — содержание письма
#           # variables — словарь переменных для подстановки:

#     def send_template_email(self, to_email, template, variables=None):
#         """
#         Отправка email по шаблону с подстановкой переменных
        
#             to_email: Email получателя
#             template: Объект шаблона Template
#             variables: Словарь переменных для подстановки
        
#         Returns:
#             bool: True если отправка успешна
#         """
#         try:
#             # Подготавливаем содержимое
#             content = template.content
#             subject = template.subject
            
#             # Подставляем переменные
#             if variables:
#                 for key, value in variables.items():
#                     placeholder = f"{{{key}}}"
#                     content = content.replace(placeholder, str(value))
#                     subject = subject.replace(placeholder, str(value))
#             print(variables)
#             print(content)
#             print(subject)

#             # Отправляем email
#             return self.send_email(
#                 to_email=to_email,
#                 subject=subject,
#                 content=content,
#                 from_email=self.smtp_username,
#                 is_html='<html>' in content.lower()  # Определяем HTML по наличию тегов
#             )
            
#         except Exception as e:
#             logger.error(f"Ошибка при отправке шаблонного email: {str(e)}")
#             return False


# class SmsService:
#     """Сервис для отправки SMS (заглушка - можно подключить реальный SMS-шлюз)"""
    
#     def send_sms(self, phone_number, message):
#         """
#         Отправка SMS
        
#         Args:
#             phone_number: Номер телефона
#             message: Текст сообщения
        
#         Returns:
#             bool: True если отправка успешна
#         """
#         try:
#             # Здесь должна быть интеграция с реальным SMS-шлюзом
#             # Например: twilio, smsc.ru, sms.ru и т.д.
            
#             # Заглушка - логируем и возвращаем успех
#             logger.info(f"SMS отправлено на {phone_number}: {message[:50]}...")
#             return True
            
#         except Exception as e:
#             logger.error(f"Ошибка при отправке SMS: {str(e)}")
#             return False
    
#     def send_template_sms(self, phone_number, template, variables=None):
#         """
#         Отправка SMS по шаблону
        
#         Args:
#             phone_number: Номер телефона
#             template: Объект шаблона Template
#             variables: Словарь переменных для подстановки
#         """
#         try:
#             message = template.sms_content
            
#             if variables:
#                 for key, value in variables.items():
#                     placeholder = f"{{{key}}}"
#                     message = message.replace(placeholder, str(value))
            
#             return self.send_sms(phone_number, message)
            
#         except Exception as e:
#             logger.error(f"Ошибка при отправке шаблонного SMS: {str(e)}")
#             return False


# class MarketingService:
#     """Основной сервис маркетинговых рассылок"""
    
#     def __init__(self):
#         self.email_service = EmailService()
#         self.sms_service = SmsService()
    
#     def send_to_recipient(self, campaign, recipient_id, client_info=None):
#         """
#         Отправка сообщения конкретному получателю
        
#         Args:
#             campaign: Объект Campaign
#             recipient_id: ID получателя
#             client_info: Информация о клиенте (если есть)
        
#         Returns:
#             tuple: (success: bool, error_message: str)
        
            

#         success, error_msg = service.send_to_recipient(
#             campaign=campaign,
#             recipient_id=recipient_id,
#             client_info=client_info
#         )
#         campaign.save()

#         """

#         from .models import CampaignRecipient
        
#         try:
#             # Получаем или создаем запись о получателе
#             recipient, created = CampaignRecipient.objects.get_or_create(
#                 campaign=campaign,
#                 recipient_id=recipient_id,
#                 defaults={
#                     'recipient_email': client_info.get('email') if client_info else '',
#                     'recipient_phone': client_info.get('phone') if client_info else '',
#                 }
#             )
            
#             # Подготавливаем переменные
#             variables = {
#                 'client_id': recipient_id,
#                 'client_name': client_info.get('name', f'Клиент #{recipient_id}') if client_info else f'Клиент #{recipient_id}',
#                 'client_email': client_info.get('email', '') if client_info else '',
#                 'manager_id': campaign.manager_id,
#                 'campaign_name': campaign.name,
#                 'date': timezone.now().strftime('%d.%m.%Y'),
#             }
            
#             success = False
#             error_msg = ""
            
#             # Отправляем в зависимости от типа шаблона

#             # получаем данные клиента 
#             if campaign.template.template_type == 'email':
#                 if not recipient.recipient_email and client_info:
#                     recipient.recipient_email = client_info.get('email', '')
#                     recipient.save()
                

#                 # почта to_email — email получателя (например: ivan@example.com)
#                 # template — объект шаблона с полями:
#                 # template.subject — тема письма
#                 # template.content — содержание письма
#                 # variables — словарь переменных для подстановки:

#                 if recipient.recipient_email:
#                     success = self.email_service.send_template_email(
#                         to_email=recipient.recipient_email,
#                         template=campaign.template,
#                         variables=variables
#                     )
#                 else:
#                     error_msg = "Email получателя отсутствует"
#                     success = False
                    
#             elif campaign.template.template_type == 'sms':
#                 if not recipient.recipient_phone and client_info:
#                     recipient.recipient_phone = client_info.get('phone', '')
#                     recipient.save()
                
#                 if recipient.recipient_phone:
#                     success = self.sms_service.send_template_sms(
#                         phone_number=recipient.recipient_phone,
#                         template=campaign.template,
#                         variables=variables
#                     )
#                 else:
#                     error_msg = "Телефон получателя отсутствует"
#                     success = False
            
#             # Обновляем статус получателя
#             if success:
#                 recipient.status = 'sent'
#                 recipient.sent_at = timezone.now()
#                 error_msg = ""
#             else:
#                 recipient.status = 'failed'
#                 recipient.error_message = error_msg or "Ошибка отправки"
            
#             recipient.save()
            
#             return success, error_msg
            
#         except Exception as e:
#             logger.error(f"Ошибка при отправке получателю {recipient_id}: {str(e)}")
#             return False, str(e)
    
#     def send_campaign(self, campaign, recipient_ids, client_info_map=None):
#         """
#         Массовая отправка кампании
        
#         Args:
#             campaign: Объект Campaign
#             recipient_ids: Список ID получателей
#             client_info_map: Словарь {recipient_id: client_info}
        
#         Returns:
#             dict: Статистика отправки
#         """
#         success_count = 0
#         failed_count = 0
#         errors = []
        
#         for recipient_id in recipient_ids:
#             client_info = client_info_map.get(recipient_id) if client_info_map else None
            
#             success, error_msg = self.send_to_recipient(
#                 campaign=campaign,
#                 recipient_id=recipient_id,
#                 client_info=client_info
#             )
            
#             if success:
#                 success_count += 1
#             else:
#                 failed_count += 1
#                 errors.append({
#                     'recipient_id': recipient_id,
#                     'error': error_msg
#                 })
        
#         # Обновляем статистику кампании
#         campaign.success_count = success_count
#         campaign.failed_count = failed_count
#         campaign.recipient_count = len(recipient_ids)
        
#         if success_count > 0:
#             campaign.status = 'sent'
#             campaign.sent_at = timezone.now()
#         else:
#             campaign.status = 'failed'
        
#         campaign.save()
        
#         return {
#             'total': len(recipient_ids),
#             'success': success_count,
#             'failed': failed_count,
#             'errors': errors
#         }


import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email через Yandex"""
    
    def __init__(self):
        # Конфигурация Yandex SMTP
        self.smtp_server = 'smtp.yandex.ru'
        self.smtp_port = 465
        self.smtp_username = 'ehsonboboev7@yandex.ru'
        self.smtp_password = 'hbewwdgiloviutid'  # В продакшене используйте переменные окружения
        
    def send_email(self, to_email, subject, content, is_html=False):
        try:
            from_email = self.smtp_username  # ТОЛЬКО EMAIL

            if is_html:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(content, 'html', 'utf-8'))
                msg.attach(MIMEText(self._strip_html(content), 'plain', 'utf-8'))
            else:
                msg = MIMEText(content, 'plain', 'utf-8')

            msg['Subject'] = subject
            msg['From'] = from_email      # ← КРИТИЧНО
            msg['To'] = to_email

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print("Успешно")

            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP ошибка: {e}")
            return False


    
    def _strip_html(self, html_content):
        """Удаляет HTML теги из текста"""
        return re.sub('<[^<]+?>', '', html_content)

    def send_template_email(self, to_email, template, variables=None):
        """
        Отправка email по шаблону с подстановкой переменных
        
        Args:
            to_email: Email получателя
            template: Объект шаблона Template
            variables: Словарь переменных для подстановки
        
        Returns:
            bool: True если отправка успешна
        """
        try:
            # Подготавливаем содержимое
            content = template.content
            subject = template.subject
            
            # Проверяем наличие необходимых переменных
            if not variables:
                variables = {}
            
            # Добавляем дефолтные значения для отсутствующих переменных
            required_vars = self._extract_placeholders(content) | self._extract_placeholders(subject)
            
            # Проверяем и заменяем все плейсхолдеры
            missing_vars = []
            for var in required_vars:
                if var not in variables:
                    missing_vars.append(var)
                    # Устанавливаем дефолтное значение
                    if var == 'name':
                        variables[var] = 'Уважаемый клиент'
                    elif var == 'client_name':
                        variables[var] = 'Клиент'
                    else:
                        variables[var] = f'[{var}]'
            
            if missing_vars:
                logger.warning(f"Отсутствующие переменные, использованы значения по умолчанию: {missing_vars}")
            
            # Подставляем переменные
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
                subject = subject.replace(placeholder, str(value))
            
            # Проверяем, что все плейсхолдеры заменены
            remaining = self._extract_placeholders(content) | self._extract_placeholders(subject)
            if remaining:
                logger.error(f"Остались незамененные плейсхолдеры: {remaining}")
                # Заменяем оставшиеся плейсхолдеры на пустые строки
                for placeholder in remaining:
                    content = content.replace(f"{{{placeholder}}}", "")
                    subject = subject.replace(f"{{{placeholder}}}", "")
            
            print("DEBUG - Переменные:", variables)
            print("DEBUG - Контент после замены:", content[:100] + "..." if len(content) > 100 else content)
            print("DEBUG - Тема после замены:", subject)

            # Определяем тип контента
            is_html = template.template_type == 'email' and ('<html>' in content.lower() or '<p>' in content or '<br>' in content)
            
            # Отправляем email
            return self.send_email(
                to_email=to_email,
                subject=subject,
                content=content,
                # from_email=f'CRM Система <{self.smtp_username}>',
                is_html=is_html
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отправке шаблонного email: {str(e)}")
            return False
    
    def _extract_placeholders(self, text):
        """Извлекает все плейсхолдеры вида {name} из текста"""
        if not text:
            return set()
        return set(re.findall(r'\{(\w+)\}', text))


class SmsService:
    """Сервис для отправки SMS (заглушка - можно подключить реальный SMS-шлюз)"""
    
    def send_sms(self, phone_number, message):
        """
        Отправка SMS
        
        Args:
            phone_number: Номер телефона
            message: Текст сообщения
        
        Returns:
            bool: True если отправка успешна
        """
        try:
            # Здесь должна быть интеграция с реальным SMS-шлюзом
            # Например: twilio, smsc.ru, sms.ru и т.д.
            
            # Заглушка - логируем и возвращаем успех
            logger.info(f"SMS отправлено на {phone_number}: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке SMS: {str(e)}")
            return False
    
    def send_template_sms(self, phone_number, template, variables=None):
        """
        Отправка SMS по шаблону
        
        Args:
            phone_number: Номер телефона
            template: Объект шаблона Template
            variables: Словарь переменных для подстановки
        """
        try:
            message = template.sms_content
            
            if variables:
                for key, value in variables.items():
                    placeholder = f"{{{key}}}"
                    message = message.replace(placeholder, str(value))
            
            return self.send_sms(phone_number, message)
            
        except Exception as e:
            logger.error(f"Ошибка при отправке шаблонного SMS: {str(e)}")
            return False


class MarketingService:
    """Основной сервис маркетинговых рассылок"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SmsService()
    
    def send_to_recipient(self, campaign, recipient_id, client_info=None):
        """
        Отправка сообщения конкретному получателю
        
        Args:
            campaign: Объект Campaign
            recipient_id: ID получателя
            client_info: Информация о клиенте (если есть)
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        from .models import CampaignRecipient
        
        try:
            # Получаем или создаем запись о получателе
            recipient, created = CampaignRecipient.objects.get_or_create(
                campaign=campaign,
                recipient_id=recipient_id,
                defaults={
                    'recipient_email': client_info.get('email') if client_info else '',
                    'recipient_phone': client_info.get('phone') if client_info else '',
                }
            )
            
            # Подготавливаем переменные - ВАЖНО: добавляем 'name' если есть 'client_name'
            variables = {
                'client_id': recipient_id,
                'client_name': client_info.get('name', f'Клиент #{recipient_id}') if client_info else f'Клиент #{recipient_id}',
                'client_email': client_info.get('email', '') if client_info else '',
                'manager_id': campaign.manager_id,
                'campaign_name': campaign.name,
                'date': timezone.now().strftime('%d.%m.%Y'),
            }
            
            # Добавляем 'name' как alias для 'client_name' (часто используется в шаблонах)
            if 'client_name' in variables:
                variables['name'] = variables['client_name']
            
            success = False
            error_msg = ""
            
            # Отправляем в зависимости от типа шаблона
            if campaign.template.template_type == 'email':
                if not recipient.recipient_email and client_info:
                    recipient.recipient_email = client_info.get('email', '')
                    recipient.save()
                
                if recipient.recipient_email:
                    success = self.email_service.send_template_email(
                        to_email=recipient.recipient_email,
                        template=campaign.template,
                        variables=variables
                    )
                    if not success:
                        error_msg = "Ошибка отправки email"
                else:
                    error_msg = "Email получателя отсутствует"
                    success = False
                    
            elif campaign.template.template_type == 'sms':
                if not recipient.recipient_phone and client_info:
                    recipient.recipient_phone = client_info.get('phone', '')
                    recipient.save()
                
                if recipient.recipient_phone:
                    success = self.sms_service.send_template_sms(
                        phone_number=recipient.recipient_phone,
                        template=campaign.template,
                        variables=variables
                    )
                else:
                    error_msg = "Телефон получателя отсутствует"
                    success = False
            
            # Обновляем статус получателя
            if success:
                recipient.status = 'sent'
                recipient.sent_at = timezone.now()
                error_msg = ""
            else:
                recipient.status = 'failed'
                recipient.error_message = error_msg or "Ошибка отправки"
            
            recipient.save()
            
            return success, error_msg
            
        except Exception as e:
            logger.error(f"Ошибка при отправке получателю {recipient_id}: {str(e)}")
            return False, str(e)
    
    def send_campaign(self, campaign, recipient_ids, client_info_map=None):
        """
        Массовая отправка кампании
        
        Args:
            campaign: Объект Campaign
            recipient_ids: Список ID получателей
            client_info_map: Словарь {recipient_id: client_info}
        
        Returns:
            dict: Статистика отправки
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for recipient_id in recipient_ids:
            client_info = client_info_map.get(recipient_id) if client_info_map else None
            
            success, error_msg = self.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_id,
                client_info=client_info
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                errors.append({
                    'recipient_id': recipient_id,
                    'error': error_msg
                })
        
        # Обновляем статистику кампании
        campaign.success_count = success_count
        campaign.failed_count = failed_count
        campaign.recipient_count = len(recipient_ids)
        
        if success_count > 0:
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
        else:
            campaign.status = 'failed'
        
        campaign.save()
        
        return {
            'total': len(recipient_ids),
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }