"""Права доступа к комнатам чата."""

from .permissions import CRM_STAFF_ROLES


def user_full_name(user) -> str:
    full = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return full or getattr(user, "email", "") or f"User {getattr(user, 'id', '')}"

# is_staff_user() — проверка на сотрудника

def is_staff_user(user) -> bool:
    return getattr(user, "role", None) in CRM_STAFF_ROLES



#  user_in_room() — участник комнаты
def user_in_room(room, user_id: int) -> bool:
    return room.participants.filter(user_id=user_id).exists()




def can_access_room(room, user) -> bool:
    #  Участник комнаты → доступ есть
    if user_in_room(room, user.id):
        return True
    
    # Сотрудник и комната из Telegram → доступ есть
    if is_staff_user(user) and hasattr(room, "telegram_binding"):
        return True
    
    # Иначе → доступа нет
    return False