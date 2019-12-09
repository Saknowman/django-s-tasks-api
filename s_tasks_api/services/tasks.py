from ..models import Task


def get_tasks(user, tasks=None):
    tasks = tasks if tasks is not None else Task.objects.all()
    return tasks.filter(created_by=user)
