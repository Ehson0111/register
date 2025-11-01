from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)

    # Роли
    ROLE_MANAGER = 'manager'
    ROLE_CLIENT = 'client'
    ROLE_CHOICES = [
        (ROLE_MANAGER, 'Менеджер'),
        (ROLE_CLIENT, 'Клиент'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CLIENT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
