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