# contacts/models.py

from django.db import models

class Contact(models.Model):
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20, blank=True)
    # можно добавить другие поля по необходимости
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
