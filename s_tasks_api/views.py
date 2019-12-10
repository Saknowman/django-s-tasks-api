from django.http import Http404
from django.utils.module_loading import import_string
from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from s_tasks_api.services.tasks import get_tasks, complete_task, un_complete_task
from s_tasks_api.settings import api_settings
from .models import Task, TaskStatus, TaskTag
from .serializers import TaskSerializer, TaskStatusSerializer, TaskTagSerializer


# noinspection PyMethodMayBeStatic
class Response403To401Mixin:
    def __init__(self):
        pass

    def permission_denied(self, request, message=None):
        if message is None:
            raise Http404
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message)


class TaskStatusViewSet(Response403To401Mixin, viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    permission_classes = [import_string(p_c) for p_c in api_settings.TASK_STATUS_PERMISSION_CLASSES]


class TaskTagViewSet(Response403To401Mixin, viewsets.ModelViewSet):
    queryset = TaskTag.objects.all()

    serializer_class = TaskTagSerializer
    permission_classes = [import_string(p_c) for p_c in api_settings.TASK_TAG_PERMISSION_CLASSES]


class TaskViewSet(Response403To401Mixin, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [import_string(p_c) for p_c in api_settings.TASK_PERMISSION_CLASSES]

    def get_queryset(self):
        return get_tasks(self.request.user, self.queryset)

    def perform_create(self, serializer):
        from s_tasks_api.services.task_status import get_task_status_from_or_default
        serializer.save(
            created_by=self.request.user,
            status=get_task_status_from_or_default(serializer.validated_data)
        )

    @action(detail=True, methods=['patch'])
    def complete(self, request, *args, **kwargs):
        task = complete_task(request.user, kwargs['pk'])
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def un_complete(self, request, *args, **kwargs):
        task = un_complete_task(request.user, kwargs['pk'])
        serializer = self.get_serializer(task)
        return Response(serializer.data)
