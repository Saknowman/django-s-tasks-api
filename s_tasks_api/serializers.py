from rest_framework import serializers

from s_tasks_api.settings import api_settings
from .models import Task, TaskStatus, TaskTag


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ('pk', 'value')
        read_only_fields = ('pk',)


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ('pk', 'value')
        read_only_fields = ('pk',)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('pk', 'title', 'detail', 'due_date', 'status', 'tag', 'created_date', 'completed', 'completed_date',
                  'created_by')
        read_only_fields = ('pk', 'created_date', 'created_by',)
        extra_kwargs = {
            'status': {'required': False}
        }
