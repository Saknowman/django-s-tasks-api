from rest_framework import serializers

from .models import Task, TaskStatus, TaskTag, GroupTask


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
            'status': {'required': False},
        }


class GroupTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.filter(), source='task', write_only=True
    )

    class Meta:
        model = GroupTask
        fields = ('pk', 'task', 'task_id', 'group', 'assignee', 'lock_level', 'assign_lock_level')
        read_only_fields = ('pk',)

    def update(self, instance, validated_data):
        """
        task and group are not changeable.
        """
        default_task = instance.task
        default_group = instance.group
        result = super().update(instance, validated_data)
        result.task = default_task
        result.group = default_group
        return result
