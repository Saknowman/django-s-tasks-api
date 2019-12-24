from typing import List
from rest_framework import permissions


class IsUserInGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'group' not in request.data:
            return True
        if not request.data['group']:
            return True
        try:
            return int(request.data['group']) in [group.pk for group in request.user.groups.all()]
        except ValueError:
            return True


class AndAll(permissions.BasePermission):
    message = None

    def __init__(self, my_permissions: List[permissions.BasePermission]):
        self._permissions = my_permissions

    def has_permission(self, request, view):
        for permission in self._permissions:
            if not permission.has_permission(request, view):
                if hasattr(permission, 'message'):
                    self.message = permission.message
                return False
        return True

    def has_object_permission(self, request, view, obj):
        for permission in self._permissions:
            if not permission.has_object_permission(request, view, obj):
                if hasattr(permission, 'message'):
                    self.message = permission.message
                return False
        return True
