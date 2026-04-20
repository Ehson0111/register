from django.db import models


CRM_STAFF_ROLES = (
    ("manager", "Manager"),
    ("admin", "Admin"),
)

CHAT_SENDER_ROLES = (
    ("manager", "Manager"),
    ("admin", "Admin"),
    ("telegram_client", "Telegram Client"),
    ("ai_assistant", "AI Assistant"),
)

CHAT_PARTICIPANT_ROLES = (
    ("manager", "Manager"),
    ("admin", "Admin"),
    ("telegram_client", "Telegram Client"),
)


class ChatRoom(models.Model):
    title = models.CharField(max_length=255, blank=True)
    created_by_id = models.PositiveIntegerField()
    created_by_email = models.EmailField(blank=True)
    created_by_name = models.CharField(max_length=255, blank=True)
    is_ai = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title or f"Chat #{self.pk}"


class ChatParticipant(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="participants")
    user_id = models.PositiveIntegerField()
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=CHAT_PARTICIPANT_ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user_id")
        ordering = ("joined_at",)

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email or f"User {self.user_id}"

    def __str__(self):
        return f"{self.room_id}:{self.user_id}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender_id = models.PositiveIntegerField()
    sender_email = models.EmailField(blank=True)
    sender_first_name = models.CharField(max_length=150, blank=True)
    sender_last_name = models.CharField(max_length=150, blank=True)
    sender_role = models.CharField(max_length=20, choices=CHAT_SENDER_ROLES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    @property
    def sender_name(self):
        full = f"{self.sender_first_name} {self.sender_last_name}".strip()
        return full or self.sender_email or f"User {self.sender_id}"

    def __str__(self):
        return f"{self.room_id}:{self.sender_id}:{self.created_at.isoformat()}"


class TelegramRoomBinding(models.Model):
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name="telegram_binding")
    telegram_chat_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    telegram_first_name = models.CharField(max_length=255, blank=True)
    telegram_last_name = models.CharField(max_length=255, blank=True)
    last_forwarded_message_id = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"tg:{self.telegram_chat_id} -> room:{self.room_id}"
