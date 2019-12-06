from rest_framework import serializers
from .models import TaskTag


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ('pk', 'value')
        read_only_fields = ('pk',)
