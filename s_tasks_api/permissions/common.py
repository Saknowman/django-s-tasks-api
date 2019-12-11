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
