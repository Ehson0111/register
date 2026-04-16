from django.db import models
from django.utils import timezone

class Applications(models.Model):
    subject = models.CharField("Тема письма", max_length=500)  # увеличил длину
    date = models.DateTimeField("Дата получения", default=timezone.now)
    text = models.TextField("Текст письма")
    sender_email = models.EmailField("Email отправителя", max_length=255, blank=True)
    message_id = models.CharField("ID письма", max_length=255, unique=True, null=True, blank=True)  # для защиты от дубликатов
    is_processed = models.BooleanField("Обработано", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.subject[:50]} - {self.date.strftime('%d.%m.%Y')}"


class ApplicationAudit(models.Model):
    ACTION_APPROVED = "approved"
    ACTION_REJECTED = "rejected"
    ACTION_PROCESSED = "processed"
    ACTIONS = [
        (ACTION_APPROVED, "Approved"),
        (ACTION_REJECTED, "Rejected"),
        (ACTION_PROCESSED, "Processed"),
    ]

    application = models.ForeignKey(
        Applications, on_delete=models.CASCADE, related_name="audits", null=True, blank=True
    )
    actor = models.CharField(max_length=255, blank=True, default="")
    action = models.CharField(max_length=32, choices=ACTIONS)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} app#{self.application_id}"


class MailboxEmail(models.Model):
    FOLDER_ALL = "all"
    FOLDER_INBOX = "inbox"
    FOLDER_SENT = "sent"
    FOLDER_IMPORTANT = "important"
    FOLDER_TRASH = "trash"

    external_id = models.CharField("Внешний ID письма", max_length=255, unique=True)
    message_id = models.CharField("Message-ID", max_length=255, blank=True, default="")
    subject = models.CharField("Тема", max_length=500, blank=True, default="")
    sender_name = models.CharField("Имя отправителя", max_length=255, blank=True, default="")
    sender_email = models.EmailField("Email отправителя", max_length=255, blank=True)
    recipients = models.TextField("Получатели", blank=True, default="")
    cc = models.TextField("Копия", blank=True, default="")
    date = models.DateTimeField("Дата письма", default=timezone.now, db_index=True)
    body_text = models.TextField("Текст письма", blank=True, default="")
    body_html = models.TextField("HTML письма", blank=True, default="")
    preview = models.TextField("Превью", blank=True, default="")
    is_read = models.BooleanField("Прочитано", default=False)
    is_important = models.BooleanField("Важное", default=False)
    in_inbox = models.BooleanField("Во входящих", default=False)
    in_sent = models.BooleanField("В отправленных", default=False)
    in_trash = models.BooleanField("В корзине", default=False)
    primary_folder = models.CharField("Основная папка", max_length=32, default=FOLDER_INBOX)
    raw_flags = models.JSONField("IMAP flags", default=list, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Почта"
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.subject[:60]} - {self.sender_email or 'unknown'}"