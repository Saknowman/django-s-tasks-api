from rest_framework import permissions

from s_tasks_api.models import Task
from s_tasks_api.services.tasks import is_my_task
from s_tasks_api.services.utils import is_in_same_group, User


class IsMyTask(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'task_id' not in request.data.keys():
            return True
        if not request.data['task_id']:
            return True
        try:
            task = Task.objects.get(pk=request.data['task_id'])
        except Task.DoesNotExist:
            return False
        return self.has_object_permission(request, view, task)

    def has_object_permission(self, request, view, obj):
        return is_my_task(request.user, obj)


class IsAssigneeInTaskGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in ['POST']:
            return True
        if 'assignee' not in request.data or \
                not request.data['assignee'] or \
                'group' not in request.data or \
                not request.data['group']:
            return True
        return is_in_same_group(request.user, User.objects.get(pk=request.data['assignee']))
