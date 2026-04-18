from rest_framework import permissions


CRM_STAFF_ROLES = frozenset({"manager", "admin"})


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in CRM_STAFF_ROLES
        )
