from rest_framework import permissions
from apps.core.constants import UserType


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "You do not have permission to perform this action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if isinstance(obj, type(request.user)):
            return obj == request.user
        
        return False


class IsVolunteer(permissions.BasePermission):
    
    message = "Only volunteers can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == UserType.VOLUNTEER
        )


class IsOrganization(permissions.BasePermission):
    
    message = "Only organizations can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == UserType.ORGANIZATION
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and (request.user.is_staff or request.user.is_superuser)
