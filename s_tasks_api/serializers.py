from rest_framework import serializers
from .models import TaskStatus, TaskTag


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
