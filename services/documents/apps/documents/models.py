from django.db import models

# Create your models here.
from django.db import models


class ClientDocument(models.Model):
    client_id = models.PositiveIntegerField(verbose_name="ID клиента")
    original_filename = models.CharField(max_length=255, verbose_name="Оригинальное имя файла")
    object_name = models.CharField(max_length=512, unique=True, verbose_name="Имя объекта в MinIO")
    content_type = models.CharField(max_length=100, blank=True, verbose_name="MIME-тип")
    file_size = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="Размер файла (байт)")
    uploaded_by = models.PositiveIntegerField(verbose_name="ID менеджера, загрузившего")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Документ клиента"
        verbose_name_plural = "Документы клиентов"
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} (client {self.client_id})"