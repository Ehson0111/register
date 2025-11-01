# # contacts/permissions.py

# from rest_framework.permissions import BasePermission

# class IsManager(BasePermission):
#     """
#     Разрешает доступ только пользователям с ролью 'manager' в JWT-токене.
#     """
#     def has_permission(self, request, view):
#         token = request.auth  # объект токена из JWTStatelessUserAuthentication
#         if not token:
#             return False
#         # Проверяем поле 'role' в полезной нагрузке токена
#         return token.get('role') == 'manager'


# class IsOwnerOrManager(BasePermission):
#     """
#     Объектное разрешение: владелец контакта или менеджер может редактировать/просматривать.
#     """
#     def has_object_permission(self, request, view, obj):
#         user = request.user
#         if not user or not user.is_authenticated:
#             return False
#         if getattr(user, 'role', None) == 'manager' or getattr(user, 'is_staff', False):
#             return True
#         # владелец контакта
#         return obj.owner_id == getattr(user, 'id', None)
from rest_framework import permissions

# class IsManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.groups.filter(name='Manager').exists() 


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
from rest_framework import permissions
class IsManager(permissions.BasePermission):
    """Доступ только для менеджеров (по твоему полю role)"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'manager'  # ← твое поле role!
        )

class IsClient(permissions.BasePermission):
    """Доступ только для клиентов"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client'  # ← твое поле role!
        )

class IsContactOwner(permissions.BasePermission):
    """Доступ только к своим контактам (по email)"""
    def has_object_permission(self, request, view, obj):
        # Клиент может доступть только контакт со своим email
        return obj.email == request.user.email