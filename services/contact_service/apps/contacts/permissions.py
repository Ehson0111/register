# contacts/permissions.py

from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Разрешает доступ только пользователям с ролью 'manager' в JWT-токене.
    """
    def has_permission(self, request, view):
        token = request.auth  # объект токена из JWTStatelessUserAuthentication
        if not token:
            return False
        # Проверяем поле 'role' в полезной нагрузке токена
        return token.get('role') == 'manager'


class IsOwnerOrManager(BasePermission):
    """
    Объектное разрешение: владелец контакта или менеджер может редактировать/просматривать.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', None) == 'manager' or getattr(user, 'is_staff', False):
            return True
        # владелец контакта
        return obj.owner_id == getattr(user, 'id', None)
