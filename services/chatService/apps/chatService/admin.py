from django.contrib import admin
from .models import ChatMessage, ChatParticipant, ChatRoom, TelegramRoomBinding


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_ai", "created_by_email", "is_active", "created_at", "updated_at")
    search_fields = ("title", "created_by_email", "created_by_name")
    list_filter = ("is_ai", "is_active", "created_at")


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user_id", "email", "role", "joined_at")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("role", "joined_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender_id", "sender_email", "sender_role", "created_at")
    search_fields = ("sender_email", "sender_first_name", "sender_last_name", "text")
    list_filter = ("sender_role", "created_at")


@admin.register(TelegramRoomBinding)
class TelegramRoomBindingAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_chat_id", "room", "telegram_username", "last_forwarded_message_id", "updated_at")
    search_fields = ("telegram_chat_id", "telegram_username", "telegram_first_name", "telegram_last_name")
    list_filter = ("created_at", "updated_at")
