# import requests
# import smtplib
# import logging
# import re
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from django.conf import settings
# from .models import CampaignRecipient
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
        
#     def send_email(self, to_email, subject, content, is_html=False):
#         try:
#             from_email = self.smtp_username  # ТОЛЬКО EMAIL

#             if is_html:
#                 msg = MIMEMultipart('alternative')
#                 msg.attach(MIMEText(content, 'html', 'utf-8'))
#                 msg.attach(MIMEText(self._strip_html(content), 'plain', 'utf-8'))
#             else:
#                 msg = MIMEText(content, 'plain', 'utf-8')

#             msg['Subject'] = subject
#             msg['From'] = from_email  
#             msg['To'] = to_email

#             with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
#                 server.login(self.smtp_username, self.smtp_password)
#                 server.send_message(msg)
#             print("Успешно")

#             return True

#         except smtplib.SMTPException as e:
#             logger.error(f"SMTP ошибка: {e}")
#             return False


    
#     def _strip_html(self, html_content):
#         """Удаляет HTML теги из текста"""
#         return re.sub('<[^<]+?>', '', html_content)

#     def send_template_email(self, to_email, template, variables=None):
#         """
#         Отправка email по шаблону с подстановкой переменных
        
#         Args:
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
            
#             # Проверяем наличие необходимых переменных
#             if not variables:
#                 variables = {}
            
#             print(variables)
            
#             # Добавляем дефолтные значения для отсутствующих переменных
#             required_vars = self._extract_placeholders(content) | self._extract_placeholders(subject)
            
#             # Проверяем и заменяем все плейсхолдеры
#             missing_vars = []
#             for var in required_vars:
#                 if var not in variables:
#                     missing_vars.append(var)
#                     # Устанавливаем дефолтное значение
#                     if var == 'name':
#                         variables[var] = 'Уважаемый клиент'
#                     elif var == 'client_name':
#                         variables[var] = 'Клиент'
#                     else:
#                         variables[var] = f'[{var}]'
            
#             if missing_vars:
#                 logger.warning(f"Отсутствующие переменные, использованы значения по умолчанию: {missing_vars}")
            
#             # Подставляем переменные
#             for key, value in variables.items():
#                 placeholder = f"{{{key}}}"
#                 content = content.replace(placeholder, str(value))
#                 subject = subject.replace(placeholder, str(value))
            
#             # Проверяем, что все плейсхолдеры заменены
#             remaining = self._extract_placeholders(content) | self._extract_placeholders(subject)
#             if remaining:
#                 logger.error(f"Остались незамененные плейсхолдеры: {remaining}")
#                 # Заменяем оставшиеся плейсхолдеры на пустые строки
#                 for placeholder in remaining:
#                     content = content.replace(f"{{{placeholder}}}", "")
#                     subject = subject.replace(f"{{{placeholder}}}", "")
            
#             print("DEBUG - Переменные:", variables)
#             print("DEBUG - Контент после замены:", content[:100] + "..." if len(content) > 100 else content)
#             print("DEBUG - Тема после замены:", subject)

#             # Определяем тип контента
#             is_html = template.template_type == 'email' and ('<html>' in content.lower() or '<p>' in content or '<br>' in content)
            
#             # Отправляем email
#             return self.send_email(
#                 to_email=to_email,
#                 subject=subject,
#                 content=content,
#                 # from_email=f'CRM Система <{self.smtp_username}>',
#                 is_html=is_html
#             )
            
#         except Exception as e:
#             logger.error(f"Ошибка при отправке шаблонного email: {str(e)}")
#             return False
    
#     def _extract_placeholders(self, text):
#         """Извлекает все плейсхолдеры вида {name} из текста"""
#         if not text:
#             return set()
#         return set(re.findall(r'\{(\w+)\}', text))


# # class SmsService:
# #     """Сервис для отправки SMS (заглушка - можно подключить реальный SMS-шлюз)"""
    
# #     def send_sms(self, phone_number, message):
# #         """
# #         Отправка SMS
        
# #         Args:
# #             phone_number: Номер телефона
# #             message: Текст сообщения
        
# #         Returns:
# #             bool: True если отправка успешна
# #         """
# #         try:
# #             # Здесь должна быть интеграция с реальным SMS-шлюзом
# #             # Например: twilio, smsc.ru, sms.ru и т.д.
            
# #             # Заглушка - логируем и возвращаем успех
# #             logger.info(f"SMS отправлено на {phone_number}: {message[:50]}...")
# #             return True
            
# #         except Exception as e:
# #             logger.error(f"Ошибка при отправке SMS: {str(e)}")
# #             return False
    
# #     def send_template_sms(self, phone_number, template, variables=None):
# #         """
# #         Отправка SMS по шаблону
        
# #         Args:
# #             phone_number: Номер телефона
# #             template: Объект шаблона Template
# #             variables: Словарь переменных для подстановки
# #         """
# #         try:
# #             message = template.sms_content
            
# #             if variables:
# #                 for key, value in variables.items():
# #                     placeholder = f"{{{key}}}"
# #                     message = message.replace(placeholder, str(value))
            
# #             return self.send_sms(phone_number, message)
            
# #         except Exception as e:
# #             logger.error(f"Ошибка при отправке шаблонного SMS: {str(e)}")
# #             return False


# class MarketingService:
#     """Основной сервис маркетинговых рассылок"""
    
#     def __init__(self):
#         self.email_service = EmailService()
#         # self.sms_service = SmsService()
    
#     # def send_to_recipient(self, campaign, recipient_id, client_info=None):
#     #     """
#     #     Отправка сообщения конкретному получателю
        
#     #     Args:
#     #         campaign: Объект Campaign
#     #         recipient_id: ID получателя
#     #         client_info: Информация о клиенте (если есть)
        
#     #     Returns:
#     #         tuple: (success: bool, error_message: str)
#     #     """
         
        
#     #     try:
#     #         # Получаем или создаем запись о получателе
#     #         recipient, created = CampaignRecipient.objects.get_or_create(
#     #             campaign=campaign,
#     #             recipient_id=recipient_id,
#     #             defaults={
#     #                 'recipient_email': client_info.get('email') if client_info else '',
#     #                 'recipient_phone': client_info.get('phone') if client_info else '',
#     #             }
#     #         )
            
#     #         # Подготавливаем переменные - ВАЖНО: добавляем 'name' если есть 'client_name'
#     #         variables = {
#     #             'client_id': recipient_id,
#     #             'client_name': client_info.get('name', f'{client_info["first_name"]}') if client_info else f'{recipient_id}',
#     #             'client_email': client_info.get('email', '') if client_info else '',
#     #             'manager_id': campaign.manager_id,
#     #             'company': campaign.name,
#     #             'date': timezone.now().strftime('%d.%m.%Y'),
#     #         }
            
#     #         # Добавляем 'nameJ' как alias для 'client_name' (часто используется в шаблонах)
#     #         if 'client_name' in variables:
#     #             variables['name'] = variables['client_name']
            
#     #         success = False
#     #         error_msg = ""
            
#     #         # Отправляем в зависимости от типа шаблона
#     #         if campaign.template.template_type == 'email':
#     #             if not recipient.recipient_email and client_info:
#     #                 recipient.recipient_email = client_info.get('email', '')
#     #                 recipient.save()
                
#     #             if recipient.recipient_email:
#     #                 success = self.email_service.send_template_email(
#     #                     to_email=recipient.recipient_email,
#     #                     template=campaign.template,
#     #                     variables=variables
#     #                 )
#     #                 if not success:
#     #                     error_msg = "Ошибка отправки email"
#     #             else:
#     #                 error_msg = "Email получателя отсутствует"
#     #                 success = False
                    
#     #         # elif campaign.template.template_type == 'sms':
#     #         #     if not recipient.recipient_phone and client_info:
#     #         #         recipient.recipient_phone = client_info.get('phone', '')
#     #         #         recipient.save()
                
#     #         #     if recipient.recipient_phone:
#     #         #         success = self.sms_service.send_template_sms(
#     #         #             phone_number=recipient.recipient_phone,
#     #         #             template=campaign.template,
#     #         #             variables=variables
#     #         #         )
#     #         #     else:
#     #         #         error_msg = "Телефон получателя отсутствует"
#     #         #         success = False
            
#     #         # Обновляем статус получателя
#     #         if success:
#     #             recipient.status = 'sent'
#     #             recipient.sent_at = timezone.now()
#     #             error_msg = ""
#     #         else:
#     #             recipient.status = 'failed'
#     #             recipient.error_message = error_msg or "Ошибка отправки"
            
#     #         recipient.save()
            
#     #         return success, error_msg
            
#     #     except Exception as e:
#     #         logger.error(f"Ошибка при отправке получателю {recipient_id}: {str(e)}")
#     #         return False, str(e)
#     def send_to_recipient(self, campaign, recipient_id, client_info=None, template_variables=None):
#         """
#         Отправка сообщения конкретному получателю
        
#         Args:
#             campaign: Объект Campaign
#             recipient_id: ID получателя
#             client_info: Информация о клиенте (если есть)
#             template_variables: Уже собранные переменные для подстановки
        
#         Returns:
#             tuple: (success: bool, error_message: str)
#         """
        
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
            
#             # ЕСЛИ variables уже переданы - используем их
#             if template_variables is not None:
#                 variables = template_variables
#             else:
#                 # Иначе собираем как раньше
#                 variables = {
#                     'client_id': recipient_id,
#                     'client_name': client_info.get('name', f'{client_info["first_name"]}') if client_info else f'{recipient_id}',
#                     'client_email': client_info.get('email', '') if client_info else '',
#                     'manager_id': campaign.manager_id,
#                     'company': campaign.name,
#                     'date': timezone.now().strftime('%d.%m.%Y'),
#                 }
                
#                 # Добавляем 'name' как alias для 'client_name'
#                 if 'client_name' in variables:
#                     variables['name'] = variables['client_name']
            
#             success = False
#             error_msg = ""
            
#             # Отправляем в зависимости от типа шаблона
#             if campaign.template.template_type == 'email':
#                 if not recipient.recipient_email and client_info:
#                     recipient.recipient_email = client_info.get('email', '')
#                     recipient.save()
                
#                 if recipient.recipient_email:
#                     success = self.email_service.send_template_email(
#                         to_email=recipient.recipient_email,
#                         template=campaign.template,
#                         variables=variables
#                     )
#                     if not success:
#                         error_msg = "Ошибка отправки email"
#                 else:
#                     error_msg = "Email получателя отсутствует"
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
        
#         def send_campaign(self, campaign, recipient_ids, client_info_map=None):
#             """
#             Массовая отправка кампании
            
#             Args:
#                 campaign: Объект Campaign
#                 recipient_ids: Список ID получателей
#                 client_info_map: Словарь {recipient_id: client_info}
            
#             Returns:
#                 dict: Статистика отправки
#             """
#             success_count = 0
#             failed_count = 0
#             errors = []
            
#             for recipient_id in recipient_ids:
#                 client_info = client_info_map.get(recipient_id) if client_info_map else None
                
#                 success, error_msg = self.send_to_recipient(
#                     campaign=campaign,
#                     recipient_id=recipient_id,
#                     client_info=client_info
#                 )
                
#                 if success:
#                     success_count += 1
#                 else:
#                     failed_count += 1
#                     errors.append({
#                         'recipient_id': recipient_id,
#                         'error': error_msg
#                     })
            
#             # Обновляем статистику кампании
#             campaign.success_count = success_count
#             campaign.failed_count = failed_count
#             campaign.recipient_count = len(recipient_ids)
            
#             if success_count > 0:
#                 campaign.status = 'sent'
#                 campaign.sent_at = timezone.now()
#             else:
#                 campaign.status = 'failed'
            
#             campaign.save()
            
#             return {
#                 'total': len(recipient_ids),
#                 'success': success_count,
#                 'failed': failed_count,
#                 'errors': errors
#             }


import requests
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from .models import CampaignRecipient, Template
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email через Yandex"""
    
    def __init__(self):
        # Конфигурация Yandex SMTP
        self.smtp_server = 'smtp.yandex.ru'
        self.smtp_port = 465
        self.smtp_username = 'ehsonboboev7@yandex.ru'
        self.smtp_password = 'hbewwdgiloviutid'
        
    def send_email(self, to_email, subject, content, is_html=False):
        try:
            from_email = self.smtp_username

            if is_html:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(content, 'html', 'utf-8'))
                msg.attach(MIMEText(self._strip_html(content), 'plain', 'utf-8'))
            else:
                msg = MIMEText(content, 'plain', 'utf-8')

            msg['Subject'] = subject
            msg['From'] = from_email  
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
        """
        try:
            # Подготавливаем содержимое
            content = template.content
            subject = template.subject
            
            # Проверяем наличие необходимых переменных
            if not variables:
                variables = {}
            
            print(variables)
            
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


class MarketingService:
    """Основной сервис маркетинговых рассылок"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def send_to_recipient(self, campaign, recipient_id, client_info=None, template_variables=None):
        """
        Отправка сообщения конкретному получателю
        """
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
            
            # ЕСЛИ variables уже переданы - используем их
            if template_variables is not None:
                variables = template_variables
            else:
                # Иначе собираем как раньше
                variables = {
                    'client_id': recipient_id,
                    'client_name': client_info.get('name', f'{client_info["first_name"]}') if client_info else f'{recipient_id}',
                    'client_email': client_info.get('email', '') if client_info else '',
                    'manager_id': campaign.manager_id,
                    'company': campaign.name,
                    'date': timezone.now().strftime('%d.%m.%Y'),
                }
                
                # Добавляем 'name' как alias для 'client_name'
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
    
    def send_campaign(self, campaign, recipient_ids, client_info_map=None, template_variables=None):
        """
        Массовая отправка кампании с шаблоном
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for recipient_id in recipient_ids:
            client_info = client_info_map.get(recipient_id) if client_info_map else None
            
            # Собираем переменные для конкретного получателя
            recipient_variables = {}
            
            # 1. Добавляем базовые переменные из client_info
            if client_info:
                recipient_variables.update({
                    'client_id': client_info.get('id', recipient_id),
                    'client_name': client_info.get('name', '') or client_info.get('client_name', ''),
                    'name': client_info.get('name', '') or client_info.get('client_name', ''),
                    'client_email': client_info.get('email', ''),
                    'phone': client_info.get('phone', ''),
                    'company': client_info.get('company', ''),
                })
            
            # 2. Добавляем общие переменные (из запроса)
            if template_variables:
                recipient_variables.update(template_variables)
            
            # 3. Добавляем системные переменные
            recipient_variables.update({
                'manager_id': campaign.manager_id,
                'date': timezone.now().strftime('%d.%m.%Y'),
                'campaign_name': campaign.name,
            })
            
            success, error_msg = self.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_id,
                client_info=client_info,
                template_variables=recipient_variables
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
    
    def send_quick_message_campaign(self, campaign, recipient_ids, client_info_map=None):
        """
        Отправка быстрой рассылки без шаблона
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for recipient_id in recipient_ids:
            client_info = client_info_map.get(recipient_id) if client_info_map else None
            
            # Для быстрых сообщений используем базовые переменные
            recipient_variables = {
                'client_id': recipient_id,
                'name': client_info.get('name', f'Клиент #{recipient_id}') if client_info else f'Клиент #{recipient_id}',
                'client_name': client_info.get('name', f'Клиент #{recipient_id}') if client_info else f'Клиент #{recipient_id}',
                'client_email': client_info.get('email', '') if client_info else '',
                'date': timezone.now().strftime('%d.%m.%Y'),
                'manager_id': campaign.manager_id,
            }
            
            success, error_msg = self.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_id,
                client_info=client_info,
                template_variables=recipient_variables
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