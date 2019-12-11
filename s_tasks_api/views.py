from django.db import transaction
from django.http import Http404
from django.utils.module_loading import import_string
from rest_framework import viewsets, exceptions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from s_tasks_api.services.tasks import get_tasks, complete_task, un_complete_task
from s_tasks_api.settings import api_settings
from .models import Task, TaskStatus, TaskTag, GroupTask
from .serializers import TaskSerializer, TaskStatusSerializer, TaskTagSerializer, GroupTaskSerializer
from .services.utils import add_items_at_query_dict


class Response403To401Mixin:
    # noinspection PyMethodMayBeStatic
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

    @action(detail=False, methods=['post'])
    def create_group_task(self, request, *args, **kwargs):
        with transaction.atomic():
            result = self.create(request, *args, **kwargs)
            if result.status_code is not status.HTTP_201_CREATED:
                return result
            task = Task.objects.get(pk=result.data['pk'])
            query_dict = add_items_at_query_dict(request.data, {'task_id': task.pk})
            group_task_serializer = GroupTaskSerializer(data=query_dict)
            group_task_serializer.is_valid(raise_exception=True)
            super().perform_create(group_task_serializer)
            headers = self.get_success_headers(group_task_serializer.data)
            return Response(group_task_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupTaskViewSet(Response403To401Mixin, viewsets.ModelViewSet):
    queryset = GroupTask.objects.all()
    serializer_class = GroupTaskSerializer
    permission_classes = [import_string(p_c) for p_c in api_settings.GROUP_TASK_PERMISSION_CLASSES]
