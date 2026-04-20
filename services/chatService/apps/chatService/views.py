from collections import defaultdict
import re
from django.db.models import Count
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from .models import ChatMessage, ChatParticipant, ChatRoom, TelegramRoomBinding
from .permissions import CRM_STAFF_ROLES, IsManagerOrAdmin
from .serializers import (
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    ChatRoomCreateSerializer,
    ChatRoomListSerializer,
    TelegramInboundMessageSerializer,
    TelegramOutboundMessageSerializer,
)


def _user_full_name(user):
    full = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return full or getattr(user, "email", "") or f"User {getattr(user, 'id', '')}"


def _can_access_room(room, user_id):
    return room.participants.filter(user_id=user_id).exists()


def _is_staff_user(user):
    return getattr(user, "role", None) in CRM_STAFF_ROLES


def _can_access_room_for_user(room, user):
    if _can_access_room(room, user.id):
        return True
    # Telegram rooms are visible to all managers/admins.
    if _is_staff_user(user) and hasattr(room, "telegram_binding"):
        return True
    return False


def _telegram_secret_valid(request):
    request_secret = request.headers.get("X-Telegram-Bridge-Secret", "")
    expected = getattr(settings, "TELEGRAM_BRIDGE_SECRET", "")
    return bool(expected and request_secret and request_secret == expected)


def _telegram_user_id(chat_id):
    # Compact deterministic id within PositiveIntegerField boundaries.
    normalized = abs(int(chat_id)) % 1_000_000_000
    return 1_000_000_000 + normalized


def _default_staff_participants():
    participant_ids = getattr(settings, "TELEGRAM_MANAGER_IDS", [])
    role_default = getattr(settings, "TELEGRAM_MANAGER_ROLE", "manager")
    participants = []
    for raw_id in participant_ids:
        try:
            user_id = int(raw_id)
        except (TypeError, ValueError):
            continue
        if user_id <= 0:
            continue
        participants.append(
            {
                "user_id": user_id,
                "role": "admin" if role_default == "admin" else "manager",
                "email": "",
                "first_name": "",
                "last_name": "",
            }
        )
    if not participants:
        participants.append(
            {
                "user_id": 1,
                "role": "manager",
                "email": "",
                "first_name": "",
                "last_name": "",
            }
        )
    return participants


def _sanitize_ai_output(text):
    if not text:
        return ""
    without_think = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    return without_think.strip()


def _build_ai_messages(room, user_text):
    system_prompt = getattr(settings, "AI_CHAT_SYSTEM_PROMPT", "").strip()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    history = list(room.messages.order_by("-created_at")[:10])
    history.reverse()
    for item in history:
        role = "assistant" if item.sender_role == "ai_assistant" else "user"
        messages.append({"role": role, "content": item.text})
    messages.append({"role": "user", "content": user_text})
    return messages


def _generate_ai_reply(room, user_text):
    if not getattr(settings, "AI_CHAT_ENABLED", False):
        return "AI-чат временно отключен в конфигурации сервиса."

    token = getattr(settings, "AI_CHAT_TOKEN", "").strip()
    endpoint = getattr(settings, "AI_CHAT_ENDPOINT", "").strip()
    model = getattr(settings, "AI_CHAT_MODEL", "").strip()
    if not token or not endpoint or not model:
        return "AI не настроен: отсутствуют AI_CHAT_TOKEN / AI_CHAT_ENDPOINT / AI_CHAT_MODEL."

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(token))
    response = client.complete(
        messages=_build_ai_messages(room, user_text),
        model=model,
        max_tokens=1024,
    )
    content = response.choices[0].message.content if response.choices else ""
    cleaned = _sanitize_ai_output(content)
    return cleaned or "Не удалось получить содержательный ответ. Попробуйте уточнить запрос."


class ChatRoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        base = ChatRoom.objects.filter(is_active=True).select_related("telegram_binding")
        if _is_staff_user(user):
            # Staff sees own rooms + all Telegram client rooms.
            base = base.filter(Q(participants__user_id=user.id) | Q(telegram_binding__isnull=False))
        else:
            base = base.filter(participants__user_id=user.id)
        return (
            base
            .annotate(messages_count=Count("messages"))
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

        participants_payload = serializer.validated_data["participants"]
        participants_by_id = {item["user_id"]: item for item in participants_payload}
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
            created_by_name=_user_full_name(actor),
        )

        participants = []
        for participant in participants_by_id.values():
            participants.append(
                ChatParticipant(
                    room=room,
                    user_id=participant["user_id"],
                    email=participant.get("email", ""),
                    first_name=participant.get("first_name", ""),
                    last_name=participant.get("last_name", ""),
                    role=participant["role"],
                )
            )
        ChatParticipant.objects.bulk_create(participants)

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
                ChatRoom.objects.filter(is_active=True, is_ai=True, participants__user_id=actor.id)
                .annotate(messages_count=Count("messages"))
                .prefetch_related("participants", "messages")
                .first()
            )
            if not room:
                room = ChatRoom.objects.create(
                    title="AI-помощник",
                    created_by_id=actor.id,
                    created_by_email=getattr(actor, "email", ""),
                    created_by_name=_user_full_name(actor),
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
        if not _can_access_room_for_user(room, request.user):
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
    queryset = ChatRoom.objects.filter(is_active=True).prefetch_related("participants", "messages").select_related("telegram_binding")
    serializer_class = ChatRoomListSerializer
    permission_classes = [IsManagerOrAdmin]

    def get_object(self):
        room = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        if not _can_access_room_for_user(room, self.request.user):
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
        if not _can_access_room_for_user(room, self.request.user):
            self.permission_denied(self.request, message="Вы не участник этого чата.")
        return room

    def get(self, request, room_id):
        room = self.get_room(room_id)
        messages = room.messages.order_by("created_at")
        return Response(ChatMessageSerializer(messages, many=True).data)

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
                ai_text = _generate_ai_reply(room, serializer.validated_data["text"])
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
    permission_classes = [AllowAny]

    def post(self, request):
        if not _telegram_secret_valid(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TelegramInboundMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        chat_id = int(payload["chat_id"])
        username = payload.get("username", "")
        first_name = payload.get("first_name", "")
        last_name = payload.get("last_name", "")

        with transaction.atomic():
            binding, created = TelegramRoomBinding.objects.select_for_update().get_or_create(
                telegram_chat_id=chat_id,
                defaults={
                    "room": ChatRoom.objects.create(
                        title=(f"Telegram @{username}" if username else f"Telegram chat {chat_id}"),
                        created_by_id=_telegram_user_id(chat_id),
                        created_by_email="",
                        created_by_name=(f"{first_name} {last_name}".strip() or username or f"Telegram {chat_id}"),
                    ),
                    "telegram_username": username,
                    "telegram_first_name": first_name,
                    "telegram_last_name": last_name,
                },
            )

            room = binding.room
            if created:
                staff_participants = _default_staff_participants()
                participant_rows = []
                for item in staff_participants:
                    participant_rows.append(
                        ChatParticipant(
                            room=room,
                            user_id=item["user_id"],
                            role=item["role"],
                            email=item.get("email", ""),
                            first_name=item.get("first_name", ""),
                            last_name=item.get("last_name", ""),
                        )
                    )
                participant_rows.append(
                    ChatParticipant(
                        room=room,
                        user_id=_telegram_user_id(chat_id),
                        role="telegram_client",
                        email="",
                        first_name=first_name or username or "Telegram",
                        last_name=last_name,
                    )
                )
                ChatParticipant.objects.bulk_create(participant_rows, ignore_conflicts=True)

            else:
                binding.telegram_username = username
                binding.telegram_first_name = first_name
                binding.telegram_last_name = last_name
                binding.save(update_fields=["telegram_username", "telegram_first_name", "telegram_last_name", "updated_at"])

            message = ChatMessage.objects.create(
                room=room,
                sender_id=_telegram_user_id(chat_id),
                sender_email="",
                sender_first_name=first_name or username or "Telegram",
                sender_last_name=last_name,
                sender_role="telegram_client",
                text=payload["text"],
            )
            room.save(update_fields=["updated_at"])

        return Response(
            {
                "ok": True,
                "room_id": room.id,
                "message_id": message.id,
            },
            status=status.HTTP_201_CREATED,
        )


class TelegramOutboundBridgeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not _telegram_secret_valid(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        limit = min(max(int(request.query_params.get("limit", 50)), 1), 200)
        outbound_items = []

        with transaction.atomic():
            bindings = list(TelegramRoomBinding.objects.select_for_update().select_related("room"))
            room_to_binding = {b.room_id: b for b in bindings}
            if not room_to_binding:
                return Response({"messages": []}, status=status.HTTP_200_OK)

            room_ids = list(room_to_binding.keys())
            min_by_room = {b.room_id: b.last_forwarded_message_id for b in bindings}

            pending = (
                ChatMessage.objects.filter(room_id__in=room_ids, sender_role__in=("manager", "admin"))
                .order_by("id")
            )

            grouped = defaultdict(list)
            for message in pending:
                if message.id > min_by_room.get(message.room_id, 0):
                    grouped[message.room_id].append(message)

            for room_id, messages in grouped.items():
                binding = room_to_binding[room_id]
                for message in messages:
                    outbound_items.append(
                        {
                            "message_id": message.id,
                            "room_id": room_id,
                            "chat_id": binding.telegram_chat_id,
                            "text": message.text,
                            "sender_name": message.sender_name,
                            "created_at": message.created_at,
                        }
                    )
                    if len(outbound_items) >= limit:
                        break
                if len(outbound_items) >= limit:
                    break

            max_forwarded_per_room = {}
            for item in outbound_items:
                room_id = item["room_id"]
                max_forwarded_per_room[room_id] = max(max_forwarded_per_room.get(room_id, 0), item["message_id"])

            for room_id, max_id in max_forwarded_per_room.items():
                binding = room_to_binding[room_id]
                binding.last_forwarded_message_id = max_id
                binding.save(update_fields=["last_forwarded_message_id", "updated_at"])

        serializer = TelegramOutboundMessageSerializer(outbound_items, many=True)
        return Response({"messages": serializer.data}, status=status.HTTP_200_OK)
