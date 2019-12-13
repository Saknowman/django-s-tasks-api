from django.utils import timezone

from ..models import Task, GroupTask


def get_task(user, pk):
    return Task.objects.filter(created_by=user, pk=pk).get()


def get_tasks(user, tasks=None):
    tasks = tasks if tasks is not None else Task.objects.all()
    return tasks.filter(created_by=user)


def get_group_tasks(user, group_tasks=None):
    group_tasks = group_tasks if group_tasks is not None else GroupTask.objects.all()
    return group_tasks.filter(group__in=[group.pk for group in user.groups.all()])


def is_my_task(user, task):
    created_user = get_created_user(task)
    return user == created_user


def is_my_group_task(user, task):
    group_task = convert_group_task(task)
    if group_task is None:
        return False
    return group_task in get_group_tasks(user)


def get_created_user(task):
    raise_if_not_task_or_group_task(task)
    if type(task) is Task:
        return task.created_by
    return task.task.created_by


# noinspection PyUnresolvedReferences
def convert_group_task(task):
    raise_if_not_task_or_group_task(task)
    if type(task) is Task:
        try:
            return task.group_task
        except Task.group_task.RelatedObjectDoesNotExist:
            return None
    return task


def raise_if_not_task_or_group_task(task):
    if type(task) in [Task, GroupTask]:
        return
    raise TypeError(
        "Except {task_type} or {group_task_type}, but {task} given.".format(task_type=Task, group_task_type=GroupTask,
                                                                            task=task))


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


def is_deletable_task(user, task):
    if is_my_task(user, task):
        return True
    task = convert_group_task(task)
    if task is None:
        return True
    return not (task.lock_level & GroupTask.DELETE_LOCK)
