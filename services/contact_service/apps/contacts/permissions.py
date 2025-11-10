 
# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.owner == request.user
from rest_framework import permissions
class IsManager(permissions.BasePermission):
    """Доступ только для менеджеров (по твоему полю role)"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'manager'  # ← поле role!
        )

class IsClient(permissions.BasePermission):
    """Доступ только для клиентов"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client'  # ← поле role!
        )

# class IsContactOwner(permissions.BasePermission):
#     """Доступ только к своим контактам (по email)"""
#     def has_object_permission(self, request, view, obj):
#         # Клиент может доступть только контакт со своим email
#         return obj.email == request.user.email