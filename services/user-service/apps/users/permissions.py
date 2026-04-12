from rest_framework import permissions

from .models import User

CRM_STAFF_ROLES = frozenset({User.ROLE_MANAGER, User.ROLE_ADMIN})


class IsManagerOrAdmin(permissions.BasePermission):
    """Менеджер или администратор CRM (доступ к панели и операциям как у менеджера)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in CRM_STAFF_ROLES
        )


class IsAdmin(permissions.BasePermission):
    """Только администратор CRM."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.ROLE_ADMIN
        )
