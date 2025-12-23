from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
import uuid

class EmailCampaign(models.Model):
    """Модель для email рассылок"""
    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_SCHEDULED, 'Запланирована'),
        (STATUS_SENDING, 'Отправляется'),
        (STATUS_SENT, 'Отправлена'),
        (STATUS_CANCELLED, 'Отменена'),
    ]
    
    TYPE_CHOICES = [
        ('promotional', 'Промо-рассылка'),
        ('newsletter', 'Новостная рассылка'),
        ('transactional', 'Транзакционное письмо'),
        ('reminder', 'Напоминание'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    campaign_type = models.CharField(
        max_length=50, 
        choices=TYPE_CHOICES, 
        default='promotional',
        verbose_name="Тип рассылки"
    )
    
    # Получатели
    target_segment = models.JSONField(default=dict, verbose_name="Сегмент получателей")
    recipient_count = models.IntegerField(default=0, verbose_name="Количество получателей")
    sent_count = models.IntegerField(default=0, verbose_name="Отправлено")
    
    # Содержимое
    subject = models.CharField(max_length=200, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    body_html = models.TextField(blank=True, verbose_name="HTML версия")
    
    # Статус и расписание
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_DRAFT,
        verbose_name="Статус"
    )
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name="Запланирована на")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Отправлена в")
    
    # Статистика
    opens_count = models.IntegerField(default=0, verbose_name="Количество открытий")
    clicks_count = models.IntegerField(default=0, verbose_name="Количество кликов")
    unsubscribes_count = models.IntegerField(default=0, verbose_name="Отписавшиеся")
    
    # Связи
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaigns',
        verbose_name="Создатель"
    )
    
    # Метаданные
    tags = models.JSONField(default=list, verbose_name="Теги")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def open_rate(self):
        """Процент открытий"""
        if self.sent_count == 0:
            return 0
        return round((self.opens_count / self.sent_count) * 100, 2)
    
    @property
    def click_rate(self):
        """Процент кликов (CTR)"""
        if self.sent_count == 0:
            return 0
        return round((self.clicks_count / self.sent_count) * 100, 2)
    
    @property
    def progress(self):
        """Прогресс отправки"""
        if self.recipient_count == 0:
            return 0
        return round((self.sent_count / self.recipient_count) * 100)
    
    @property
    def is_active_campaign(self):
        """Активна ли рассылка"""
        return self.status in [self.STATUS_SCHEDULED, self.STATUS_SENDING]


class EmailTemplate(models.Model):
    """Шаблоны email писем"""
    CATEGORY_CHOICES = [
        ('welcome', 'Приветственное'),
        ('promotional', 'Промо'),
        ('newsletter', 'Новости'),
        ('transactional', 'Транзакционное'),
        ('reminder', 'Напоминание'),
        ('notification', 'Уведомление'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='promotional',
        verbose_name="Категория"
    )
    
    # Контент
    subject = models.CharField(max_length=200, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Шаблон письма")
    body_html = models.TextField(blank=True, verbose_name="HTML шаблон")
    
    # Переменные для шаблона
    variables = models.JSONField(
        default=list,
        verbose_name="Доступные переменные",
        help_text="Список переменных для подстановки: {{имя}}"
    )
    
    # Статистика использования
    used_count = models.IntegerField(default=0, verbose_name="Использований")
    
    # Метаданные
    tags = models.JSONField(default=list, verbose_name="Теги")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_templates',
        verbose_name="Создатель"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Шаблон письма"
        verbose_name_plural = "Шаблоны писем"
    
    def __str__(self):
        return self.name


class ContactSegment(models.Model):
    """Сегменты контактов для рассылок"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Название сегмента")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Правила фильтрации
    filters = models.JSONField(
        default=dict,
        verbose_name="Фильтры",
        help_text="JSON с правилами фильтрации контактов"
    )
    
    # Результаты фильтрации
    contact_count = models.IntegerField(default=0, verbose_name="Количество контактов")
    last_calculated_at = models.DateTimeField(null=True, blank=True, verbose_name="Последний расчет")
    
    # Метаданные
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contact_segments',
        verbose_name="Создатель"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Сегмент контактов"
        verbose_name_plural = "Сегменты контактов"
    
    def __str__(self):
        return f"{self.name} ({self.contact_count} контактов)"


class CampaignStatistic(models.Model):
    """Детальная статистика по кампаниям"""
    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name="Рассылка"
    )
    
    date = models.DateField(verbose_name="Дата")
    
    # Статистика за день
    sent = models.IntegerField(default=0, verbose_name="Отправлено")
    delivered = models.IntegerField(default=0, verbose_name="Доставлено")
    opened = models.IntegerField(default=0, verbose_name="Открыто")
    clicked = models.IntegerField(default=0, verbose_name="Кликов")
    unsubscribed = models.IntegerField(default=0, verbose_name="Отписались")
    bounced = models.IntegerField(default=0, verbose_name="Возвратов")
    complaints = models.IntegerField(default=0, verbose_name="Жалоб")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['campaign', 'date']
        ordering = ['-date']
        verbose_name = "Статистика рассылки"
        verbose_name_plural = "Статистика рассылок"
    
    def __str__(self):
        return f"{self.campaign.name} - {self.date}"
    
    @property
    def open_rate(self):
        if self.delivered == 0:
            return 0
        return round((self.opened / self.delivered) * 100, 2)
    
    @property
    def click_rate(self):
        if self.delivered == 0:
            return 0
        return round((self.clicked / self.delivered) * 100, 2)


class Unsubscribe(models.Model):
    """Отписки от рассылок"""
    REASON_CHOICES = [
        ('not_interested', 'Не интересно'),
        ('too_frequent', 'Слишком часто'),
        ('content', 'Не нравится контент'),
        ('other', 'Другое'),
    ]
    
    email = models.EmailField(verbose_name="Email")
    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='unsubscribes',
        verbose_name="Рассылка"
    )
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        default='not_interested',
        verbose_name="Причина"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['email', 'campaign']
        ordering = ['-created_at']
        verbose_name = "Отписка"
        verbose_name_plural = "Отписки"
    
    def __str__(self):
        return f"{self.email} - {self.campaign.name}"