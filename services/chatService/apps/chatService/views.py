from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_service import generate_ai_reply
from .models import ChatMessage, ChatParticipant, ChatRoom
from .permissions import CRM_STAFF_ROLES, IsManagerOrAdmin
from .room_access import can_access_room, is_staff_user, user_full_name
from .serializers import (
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    ChatRoomCreateSerializer,
    ChatRoomListSerializer,
    TelegramInboundMessageSerializer,
    TelegramOutboundMessageSerializer,
)
from .telegram_service import (
    fetch_outbound_messages,
    process_inbound_message,
    telegram_secret_valid,
)


class ChatRoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        base = ChatRoom.objects.filter(is_active=True).select_related("telegram_binding")
        if is_staff_user(user):
            base = base.filter(
                Q(participants__user_id=user.id) | Q(telegram_binding__isnull=False)
            )
        else:
            base = base.filter(participants__user_id=user.id)
        return (
            base.annotate(messages_count=Count("messages"))
            .prefetch_related("participants", "messages")
            .distinct()
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ChatRoomCreateSerializer
        return ChatRoomListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actor = request.user
        actor_role = getattr(actor, "role", None)
        if actor_role not in CRM_STAFF_ROLES:
            return Response({"detail": "Недостаточно прав."}, status=status.HTTP_403_FORBIDDEN)

        participants_by_id = {
            item["user_id"]: item for item in serializer.validated_data["participants"]
        }
        participants_by_id[actor.id] = {
            "user_id": actor.id,
            "role": actor_role,
            "email": getattr(actor, "email", ""),
            "first_name": getattr(actor, "first_name", ""),
            "last_name": getattr(actor, "last_name", ""),
        }

        room = ChatRoom.objects.create(
            title=serializer.validated_data.get("title", "").strip(),
            created_by_id=actor.id,
            created_by_email=getattr(actor, "email", ""),
            created_by_name=user_full_name(actor),
        )
        ChatParticipant.objects.bulk_create(
            [
                ChatParticipant(
                    room=room,
                    user_id=p["user_id"],
                    email=p.get("email", ""),
                    first_name=p.get("first_name", ""),
                    last_name=p.get("last_name", ""),
                    role=p["role"],
                )
                for p in participants_by_id.values()
            ]
        )

        output = (
            ChatRoom.objects.filter(id=room.id)
            .annotate(messages_count=Count("messages"))
            .prefetch_related("participants", "messages")
            .first()
        )
        return Response(ChatRoomListSerializer(output).data, status=status.HTTP_201_CREATED)


class ChatAIRoomEnsureView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request):
        actor = request.user
        actor_role = getattr(actor, "role", None)
        if actor_role not in CRM_STAFF_ROLES:
            return Response({"detail": "Недостаточно прав."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            room = (
                ChatRoom.objects.filter(
                    is_active=True, is_ai=True, participants__user_id=actor.id
                )
                .annotate(messages_count=Count("messages"))
                .prefetch_related("participants", "messages")
                .first()
            )
            if not room:
                room = ChatRoom.objects.create(
                    title="AI-помощник",
                    created_by_id=actor.id,
                    created_by_email=getattr(actor, "email", ""),
                    created_by_name=user_full_name(actor),
                    is_ai=True,
                )
                ChatParticipant.objects.create(
                    room=room,
                    user_id=actor.id,
                    email=getattr(actor, "email", ""),
                    first_name=getattr(actor, "first_name", ""),
                    last_name=getattr(actor, "last_name", ""),
                    role=actor_role,
                )
                ChatMessage.objects.create(
                    room=room,
                    sender_id=0,
                    sender_email="",
                    sender_first_name="AI",
                    sender_last_name="Assistant",
                    sender_role="ai_assistant",
                    text=(
                        "Привет! Я AI-помощник в CRM.\n"
                        "Могу помочь с текстами, письмами, документами, KPI и скриптами продаж.\n"
                        "Например: 'Сделай шаблон коммерческого предложения для клиента'."
                    ),
                )
                room.save(update_fields=["updated_at"])

        output = (
            ChatRoom.objects.filter(id=room.id)
            .annotate(messages_count=Count("messages"))
            .prefetch_related("participants", "messages")
            .first()
        )
        return Response(ChatRoomListSerializer(output).data, status=status.HTTP_200_OK)


class ChatAIRoomResetContextView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, room_id):
        room = get_object_or_404(
            ChatRoom.objects.prefetch_related("participants"),
            pk=room_id,
            is_active=True,
            is_ai=True,
        )
        if not can_access_room(room, request.user):
            self.permission_denied(request, message="Вы не участник этого чата.")

        with transaction.atomic():
            room.messages.all().delete()
            welcome = ChatMessage.objects.create(
                room=room,
                sender_id=0,
                sender_email="",
                sender_first_name="AI",
                sender_last_name="Assistant",
                sender_role="ai_assistant",
                text=(
                    "Контекст очищен.\n"
                    "Готов начать заново. Опиши задачу или выбери подсказку."
                ),
            )
            room.save(update_fields=["updated_at"])

        return Response(
            {
                "ok": True,
                "room_id": room.id,
                "message": ChatMessageSerializer(welcome).data,
            },
            status=status.HTTP_200_OK,
        )


class ChatRoomDetailView(generics.RetrieveDestroyAPIView):
    queryset = (
        ChatRoom.objects.filter(is_active=True)
        .prefetch_related("participants", "messages")
        .select_related("telegram_binding")
    )
    serializer_class = ChatRoomListSerializer
    permission_classes = [IsManagerOrAdmin]

    def get_object(self):
        room = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        if not can_access_room(room, self.request.user):
            self.permission_denied(self.request, message="Вы не участник этого чата.")
        return room

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.is_active = False
        room.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatMessageListCreateView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get_room(self, room_id):
        room = get_object_or_404(
            ChatRoom.objects.select_related("telegram_binding"),
            pk=room_id,
            is_active=True,
        )
        if not can_access_room(room, self.request.user):
            self.permission_denied(self.request, message="Вы не участник этого чата.")
        return room

    def get(self, request, room_id):
        room = self.get_room(room_id)
        return Response(
            ChatMessageSerializer(room.messages.order_by("created_at"), many=True).data
        )

    def post(self, request, room_id):
        room = self.get_room(room_id)
        serializer = ChatMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user_role = getattr(user, "role", None)
        if user_role not in CRM_STAFF_ROLES:
            return Response({"detail": "Недостаточно прав."}, status=status.HTTP_403_FORBIDDEN)

        message = ChatMessage.objects.create(
            room=room,
            sender_id=user.id,
            sender_email=getattr(user, "email", ""),
            sender_first_name=getattr(user, "first_name", ""),
            sender_last_name=getattr(user, "last_name", ""),
            sender_role=user_role,
            text=serializer.validated_data["text"],
        )

        ai_error = None
        if room.is_ai:
            try:
                ai_text = generate_ai_reply(room, serializer.validated_data["text"])
                ChatMessage.objects.create(
                    room=room,
                    sender_id=0,
                    sender_email="",
                    sender_first_name="AI",
                    sender_last_name="Assistant",
                    sender_role="ai_assistant",
                    text=ai_text,
                )
            except Exception as exc:
                ai_error = str(exc)
                ChatMessage.objects.create(
                    room=room,
                    sender_id=0,
                    sender_email="",
                    sender_first_name="AI",
                    sender_last_name="Assistant",
                    sender_role="ai_assistant",
                    text="Не удалось получить ответ от AI. Попробуйте еще раз через несколько секунд.",
                )

        room.save(update_fields=["updated_at"])
        payload = ChatMessageSerializer(message).data
        if ai_error:
            payload["ai_error"] = ai_error
        return Response(payload, status=status.HTTP_201_CREATED)


class TelegramInboundBridgeView(APIView):
    """POST от tgbots: входящее сообщение клиента."""

    permission_classes = [AllowAny]

    def post(self, request):
        if not telegram_secret_valid(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TelegramInboundMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_inbound_message(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)


class TelegramOutboundBridgeView(APIView):
    """GET от tgbots: очередь ответов менеджеров для sendMessage."""

    permission_classes = [AllowAny]

    def get(self, request):
        if not telegram_secret_valid(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        limit = min(max(int(request.query_params.get("limit", 50)), 1), 200)
        outbound = fetch_outbound_messages(limit)
        serializer = TelegramOutboundMessageSerializer(outbound, many=True)
        return Response({"messages": serializer.data}, status=status.HTTP_200_OK)
