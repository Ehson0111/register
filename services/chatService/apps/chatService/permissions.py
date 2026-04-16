from rest_framework import permissions

CRM_STAFF_ROLES = frozenset({"manager", "admin"})


class IsManagerOrAdmin(permissions.BasePermission):
    """Доступ только для менеджеров и админов CRM."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in CRM_STAFF_ROLES
        )
