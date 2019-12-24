from rest_framework import permissions


class OnlyAdminCanChange(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            return request.user.is_superuser
        return True
