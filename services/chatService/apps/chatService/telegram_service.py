"""
Telegram-мост: комнаты, привязка chat_id, очередь исходящих для tgbots.
"""

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import ChatMessage, ChatParticipant, ChatRoom, TelegramRoomBinding


def telegram_secret_valid(request) -> bool:
    # Проверяет, что запрос пришёл от доверенного источника (tgbots).


    request_secret = request.headers.get("X-Telegram-Bridge-Secret", "")
    expected = getattr(settings, "TELEGRAM_BRIDGE_SECRET", "")
    return bool(expected and request_secret and request_secret == expected)


def telegram_user_id(chat_id: int) -> int:
    """  user_id для клиента Telegram chat_id = 123456789123456789
normalized = 123456789 % 1_000_000_000 = 123456789
результат = 1_000_000_000 + 123456789 = 1123456789 (PositiveIntegerField)."""
    normalized = abs(int(chat_id)) % 1_000_000_000
    return 1_000_000_000 + normalized

#   Берёт из настроек список менеджеров, 
# которые автоматически добавляются в каждый новый Telegram-чат.


def default_staff_participants() -> list[dict]:
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


def process_inbound_message(payload: dict) -> dict:
    """
    Сообщение из tgbots → комната CRM + ChatMessage.
    Вызывается из TelegramInboundBridgeView.
    """
    chat_id = int(payload["chat_id"])
    username = payload.get("username", "")
    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")

    with transaction.atomic():
        binding, created = TelegramRoomBinding.objects.select_for_update().get_or_create(
            telegram_chat_id=chat_id,
            defaults={
                "room": ChatRoom.objects.create(
                    title=(
                        f"Telegram @{username}"
                        if username
                        else f"Telegram chat {chat_id}"
                    ),
                    created_by_id=telegram_user_id(chat_id),
                    created_by_email="",
                    created_by_name=(
                        f"{first_name} {last_name}".strip()
                        or username
                        or f"Telegram {chat_id}"
                    ),
                ),
                "telegram_username": username,
                "telegram_first_name": first_name,
                "telegram_last_name": last_name,
            },
        )

        room = binding.room
        # Если комната новая — добавить участников:


        if created:
                # Добавляем менеджеров

            rows = [
                ChatParticipant(
                    room=room,
                    user_id=item["user_id"],
                    role=item["role"],
                    email=item.get("email", ""),
                    first_name=item.get("first_name", ""),
                    last_name=item.get("last_name", ""),
                )
                for item in default_staff_participants()
            ]
                # Добавляем самого клиента из Telegram

            
            rows.append(
                ChatParticipant(
                    room=room,
                    user_id=telegram_user_id(chat_id),
                    role="telegram_client",
                    email="",
                    first_name=first_name or username or "Telegram",
                    last_name=last_name,
                )
            )
            ChatParticipant.objects.bulk_create(rows, ignore_conflicts=True)
        else:
            binding.telegram_username = username
            binding.telegram_first_name = first_name
            binding.telegram_last_name = last_name
            binding.save(
                update_fields=[
                    "telegram_username",
                    "telegram_first_name",
                    "telegram_last_name",
                    "updated_at",
                ]
            )
        # Сохранить сообщение:
 

        message = ChatMessage.objects.create(
            room=room,
            sender_id=telegram_user_id(chat_id),
            sender_email="",
            sender_first_name=first_name or username or "Telegram",
            sender_last_name=last_name,
            sender_role="telegram_client",
            text=payload["text"],
        )
        room.save(update_fields=["updated_at"])

    return {"ok": True, "room_id": room.id, "message_id": message.id}


def fetch_outbound_messages(limit: int) -> list[dict]:
    """
    Сообщения менеджеров, ещё не переданные в Telegram.
    id > last_forwarded_message_id — один ORM-запрос вместо цикла по всем сообщениям.
    """
    with transaction.atomic(): # Если ЛЮБАЯ операция внутри блока упадёт с ошибкой → все изменения откатываются. БД остаётся в целостном состоянии.
        pending = list(
            ChatMessage.objects.filter(
                room__telegram_binding__isnull=False, # комната привязана к Telegram
                sender_role__in=("manager", "admin"),  # только менеджеры/админы

                id__gt=F("room__telegram_binding__last_forwarded_message_id"), # ещё не отправлено
            )
            .select_related("room__telegram_binding")
            .order_by("id")[:limit]
        )
        if not pending:
            return []

        outbound = []
        max_id_by_room: dict[int, int] = {}
        for message in pending:
            binding = message.room.telegram_binding
            outbound.append(
                {
                    "message_id": message.id,
                    "room_id": message.room_id,
                    "chat_id": binding.telegram_chat_id,
                    "text": message.text,
                    "sender_name": message.sender_name,
                    "created_at": message.created_at,
                }
            )
            max_id_by_room[message.room_id] = max(
                max_id_by_room.get(message.room_id, 0), message.id
            )

        now = timezone.now()
        for room_id, max_id in max_id_by_room.items():
            TelegramRoomBinding.objects.filter(room_id=room_id).update(
                last_forwarded_message_id=max_id,
                updated_at=now,
            )

        return outbound
