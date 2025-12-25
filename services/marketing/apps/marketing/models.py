from django.utils import timezone
from django.db import models

# Create your models here.
# 1 шаблон рассылок 
# 2 id пользователей 
# 3 запланированное время рассылки  
# class MarketingTemplate(models.Model):
#     name = models.CharField(max_length=100, verbose_name="Название шаблона")
#     subject = models.CharField(max_length=200, verbose_name="Тема письма")
#     body = models.TextField(verbose_name="Тело письма")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

#     def __str__(self):
#         return self.name


# class MarketingCampaign(models.Model):
#     template = models.ForeignKey(MarketingTemplate, on_delete=models.CASCADE, related_name='campaigns', verbose_name="Шаблон рассылки")
#     user_ids = models.TextField(verbose_name="ID пользователей для рассылки")  # Список ID пользователей через запятую
#     scheduled_time = models.DateTimeField(verbose_name="Запланированное время рассылки")
#     sent = models.BooleanField(default=False, verbose_name="Отправлено")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

#     def __str__(self):
#         return f"Campaign {self.id} using {self.template.name}"
 
class Template(models.Model):
    # name = models.CharField(max_length=100, verbose_name="Название шаблона")
    # subject = models.CharField(max_length=200, verbose_name="Тема письма")
    # body = models.TextField(verbose_name="Тело письма")
    # created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    # updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # def __str__(self):
    #     return self.name
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Название шаблона")
    template_types=models.CharField(max_length=10,choices=TEMPLATE_TYPES,default="email")


    # Для email
    subject = models.CharField(max_length=255, blank=True, verbose_name="Тема")
    content = models.TextField(verbose_name="Содержание")
    
    # Для SMS
    sms_content = models.CharField(max_length=500, blank=True, verbose_name="Текст SMS")
    
    # Общие поля
    variables = models.JSONField(default=list, verbose_name="Доступные переменные")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Владелец
    manager_id = models.IntegerField(verbose_name="ID менеджера")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class meta:
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['manager_id', 'template_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    ]

    CAMPAIGN_TYPES=[ 

       ('individual', 'Индивидуальная'),
        ('bulk', 'Массовая')
    ]

    name =models.CharField(max_length=200,verbose_name="Название кампании")
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='individual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Шаблон
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, 
                                verbose_name="Шаблон", related_name='campaigns')
    
    # Содержание (может отличаться от шаблона)
    subject = models.CharField(max_length=255, blank=True, verbose_name="Тема")
    content = models.TextField(verbose_name="Содержание")
    
    # Получатели
    recipients = models.JSONField(default=list, verbose_name="ID получателей")
    recipient_count = models.IntegerField(default=0, verbose_name="Количество получателей")
    
    # Время
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Время отправки")
    
    # Статистика
    success_count = models.IntegerField(default=0, verbose_name="Успешно отправлено")
    failed_count = models.IntegerField(default=0, verbose_name="Не отправлено")
    
    # Менеджер
    manager_id = models.IntegerField(verbose_name="ID менеджера")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at','-sent_at']
        indexes = [
            models.Index(fields=['manager_id', 'status']),
            models.Index(fields=['-sent_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})" 
    


class CampaignRecipient(models.Model):
    """Информация о каждом получателе в кампании"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('opened', 'Открыто'),
        ('failed', 'Ошибка'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, 
                                related_name='campaign_recipients')
    recipient_id = models.IntegerField(verbose_name="ID получателя")
    recipient_email = models.EmailField(blank=True, verbose_name="Email получателя")
    recipient_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон получателя")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(blank=True, verbose_name="Сообщение об ошибке")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['campaign', 'recipient_id']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['recipient_id']),
        ]
    
    def __str__(self):
        return f"Получатель {self.recipient_id} в кампании {self.campaign.name}"