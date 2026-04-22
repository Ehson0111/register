from rest_framework.permissions import BasePermission


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        role = getattr(user, "role", None)
        return bool(user and getattr(user, "is_authenticated", False) and role in ("manager", "admin"))
