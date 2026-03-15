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