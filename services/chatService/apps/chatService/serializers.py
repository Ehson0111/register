from rest_framework import serializers

from .models import ChatMessage, ChatParticipant, ChatRoom, TelegramRoomBinding


class ChatParticipantSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = (
            "id",
            "user_id",
            "email",
            "first_name",
            "last_name",
            "role",
            "full_name",
            "joined_at",
        )
        read_only_fields = ("id", "joined_at", "full_name")


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "room",
            "sender_id",
            "sender_email",
            "sender_first_name",
            "sender_last_name",
            "sender_role",
            "sender_name",
            "text",
            "created_at",
        )
        read_only_fields = (
            "id",
            "room",
            "sender_id",
            "sender_email",
            "sender_first_name",
            "sender_last_name",
            "sender_role",
            "sender_name",
            "created_at",
        )


class ChatRoomListSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    messages_count = serializers.IntegerField(read_only=True)
    is_telegram = serializers.SerializerMethodField()
    telegram_chat_id = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "title",
            "created_by_id",
            "created_by_email",
            "created_by_name",
            "is_ai",
            "is_active",
            "created_at",
            "updated_at",
            "messages_count",
            "last_message",
            "is_telegram",
            "telegram_chat_id",
            "participants",
        )
        read_only_fields = (
            "id",
            "created_by_id",
            "created_by_email",
            "created_by_name",
            "is_ai",
            "created_at",
            "updated_at",
            "messages_count",
            "last_message",
            "is_telegram",
            "telegram_chat_id",
            "participants",
        )

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()
        if not message:
            return None
        return ChatMessageSerializer(message).data

    def get_is_telegram(self, obj):
        return hasattr(obj, "telegram_binding")

    def get_telegram_chat_id(self, obj):
        binding = getattr(obj, "telegram_binding", None)
        if isinstance(binding, TelegramRoomBinding):
            return binding.telegram_chat_id
        return None


class ChatRoomCreateSerializer(serializers.Serializer):
    class ParticipantInputSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(min_value=1)
        role = serializers.ChoiceField(choices=("manager", "admin"))
        email = serializers.EmailField(required=False, allow_blank=True)
        first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
        last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    participants = serializers.ListField(
        child=ParticipantInputSerializer(),
        allow_empty=False,
        write_only=True,
    )

    def validate_participants(self, value):
        unique_by_id = {}
        for item in value:
            unique_by_id[item["user_id"]] = item
        unique_items = list(unique_by_id.values())
        if len(unique_items) < 2:
            raise serializers.ValidationError("Чат должен содержать минимум 2 участников.")
        return unique_items


class ChatMessageCreateSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=False, trim_whitespace=True, max_length=5000)


class TelegramInboundMessageSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    text = serializers.CharField(allow_blank=False, trim_whitespace=True, max_length=5000)
    username = serializers.CharField(required=False, allow_blank=True, max_length=255)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=255)


class TelegramOutboundMessageSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    room_id = serializers.IntegerField()
    chat_id = serializers.IntegerField()
    text = serializers.CharField()
    sender_name = serializers.CharField()
    created_at = serializers.DateTimeField()
