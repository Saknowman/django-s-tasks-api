from django.utils import timezone

from ..models import Task


def get_task(user, pk):
    return Task.objects.filter(created_by=user, pk=pk).get()


def get_tasks(user, tasks=None):
    tasks = tasks if tasks is not None else Task.objects.all()
    return tasks.filter(created_by=user)


def complete_task(user, pk):
    task = get_task(user, pk)
    if task.completed:
        return task
    task.completed = True
    task.completed_date = timezone.now().date()
    task.save()
    return task


def un_complete_task(user, pk):
    task = get_task(user, pk)
    if not task.completed:
        return task
    task.completed = False
    task.completed_date = None
    task.save()
    return task
