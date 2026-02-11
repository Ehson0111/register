from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    PURPOSE_REGISTER = "register"
    PURPOSE_RESET = "reset"
    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, "Registration verification"),
        (PURPOSE_RESET, "Password reset"),
    ]

    email = models.EmailField(db_index=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    used = models.BooleanField(default=False, db_index=True)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["email", "purpose", "used"]),
            models.Index(fields=["expires_at"]),
        ]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

