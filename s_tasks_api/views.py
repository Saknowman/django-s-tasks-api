from django.http import Http404
from django.utils.module_loading import import_string
from rest_framework import viewsets, exceptions

from s_tasks_api.settings import api_settings
from .models import TaskTag
from .serializers import TaskTagSerializer


class Response403To401Mixin:
    def permission_denied(self, request, message=None):
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()
        if message is None:
            raise Http404
        raise exceptions.PermissionDenied(detail=message)


class TaskTagViewSet(Response403To401Mixin, viewsets.ModelViewSet):
    queryset = TaskTag.objects.all()

    serializer_class = TaskTagSerializer
    permission_classes = [import_string(p_c) for p_c in api_settings.TASK_TAG_PERMISSION_CLASSES]
