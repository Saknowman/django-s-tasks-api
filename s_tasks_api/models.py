from django.db import models
from django.conf import settings

from .settings import api_settings


class TaskTag(models.Model):
    value = models.CharField(max_length=api_settings.TASK_TAG_MODEL['MAX_LENGTH'], unique=True)

    def __str__(self):
        return self.value


class TaskStatus(models.Model):
    value = models.CharField(max_length=api_settings.TASK_STATUS_MODEL['MAX_LENGTH'], unique=True)

    def __str__(self):
        return self.value


class Task(models.Model):
    title = models.CharField(max_length=api_settings.TASK_MODEL['TITLE_MAX_LENGTH'],
                             default=api_settings.TASK_MODEL['TITLE_DEFAULT'])
    detail = models.TextField(default=api_settings.TASK_MODEL['DETAIL_DEFAULT'])
    due_date = models.DateField(blank=True, null=True)
    status = models.ForeignKey(to=TaskStatus, related_name='todo_tasks', on_delete=models.PROTECT)
    tag = models.ForeignKey(to=TaskTag, blank=True, null=True, related_name='todo_tasks', on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "{tag}/{title}:{status}".format(title=self.title, status=self.status, tag=self.tag)
