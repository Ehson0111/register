 
from rest_framework import permissions

CRM_STAFF_ROLES = frozenset({'manager', 'admin'})


class IsManager(permissions.BasePermission):
    """Менеджер или администратор CRM (поле role в JWT)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) in CRM_STAFF_ROLES
        )

class IsClient(permissions.BasePermission):
    """Доступ только для клиентов"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client'  # ← поле role!
        )
