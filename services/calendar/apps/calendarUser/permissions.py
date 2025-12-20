from rest_framework import permissions
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
                    request.user and
                    request.user.is_authenticated and 
                    request.user.role =='manager'
                    )
    
class IsClient(permissions.BasePermission):
    """Доступ только для клиентов"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client'  
        )