from django.contrib.auth.models import Group
from django.core import validators
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


class GroupTask(models.Model):
    # Task Lock Level
    NON_LOCK = 0b0
    TITLE_LOCK = 0b1
    DETAIL_LOCK = 0b1 << 1
    DUE_DATE_LOCK = 0b1 << 2
    STATUS_LOCK = 0b1 << 3
    TAG_LOCK = 0b1 << 4
    COMPLETED_LOCK = 0b1 << 5
    DELETE_LOCK = 0b1 << 6
    FULL_LOCK = NON_LOCK | TITLE_LOCK | DETAIL_LOCK | DUE_DATE_LOCK | STATUS_LOCK | TAG_LOCK | COMPLETED_LOCK | DELETE_LOCK

    # Assign Lock Level
    ASSIGN_LOCK_NON = 0b0
    ASSIGN_LOCK_MEMBERS = 0b1
    ASSIGN_LOCK_ASSIGNEE = 0b1 << 1
    ASSIGN_LOCK_CREATED_USER = 0b1 << 2
    ASSIGN_FULL_LOCK = ASSIGN_LOCK_MEMBERS | ASSIGN_LOCK_ASSIGNEE | ASSIGN_LOCK_CREATED_USER

    task = models.OneToOneField(to=Task, related_name='group_task', on_delete=models.CASCADE)
    group = models.ForeignKey(to=Group, related_name='group_tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, default=None,
                                 on_delete=models.SET_DEFAULT)
    lock_level = models.IntegerField(default=NON_LOCK, validators=[
        validators.MinValueValidator(NON_LOCK),
        validators.MaxValueValidator(FULL_LOCK)
    ])
    assign_lock_level = models.IntegerField(default=ASSIGN_LOCK_NON, validators=[
        validators.MinValueValidator(ASSIGN_LOCK_NON),
        validators.MaxValueValidator(ASSIGN_FULL_LOCK)
    ])

    LOCK_LEVELS = {
        'NON_LOCK': NON_LOCK,
        'TITLE_LOCK': TITLE_LOCK,
        'DETAIL_LOCK': DETAIL_LOCK,
        'DUE_DATE_LOCK': DUE_DATE_LOCK,
        'STATUS_LOCK': STATUS_LOCK,
        'TAG_LOCK': TAG_LOCK,
        'COMPLETED_LOCK': COMPLETED_LOCK,
        'DELETE_LOCK': DELETE_LOCK,
        'FULL_LOCK': FULL_LOCK,
    }

    ASSIGN_LOCK_LEVELS = {
        'ASSIGN_LOCK_NON': ASSIGN_LOCK_NON,
        'ASSIGN_LOCK_MEMBERS': ASSIGN_LOCK_MEMBERS,
        'ASSIGN_LOCK_ASSIGNEE': ASSIGN_LOCK_ASSIGNEE,
        'ASSIGN_LOCK_CREATED_USER': ASSIGN_LOCK_CREATED_USER,
        'ASSIGN_FULL_LOCK': ASSIGN_FULL_LOCK,
    }

    def __str__(self):
        return self.group.name + ':' + self.task.title
