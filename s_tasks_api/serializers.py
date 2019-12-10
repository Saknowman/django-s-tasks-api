from rest_framework import serializers

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
        fields = ('pk', 'title', 'detail', 'due_date', 'status', 'tag', 'created_date',
                  'created_by')
        read_only_fields = ('pk', 'completed', 'completed_date', 'created_date', 'created_by',)
        extra_kwargs = {
            'title': {'required': True},
            'status': {'required': False}
        }
