from django.utils import timezone
from django.db.models import Q
from ..models import Task, GroupTask


def get_task(user, pk):
    task = Task.objects.filter(pk=pk).get()
    if is_task_created_by(user, task) or is_my_group_task(user, task):
        return task
    raise Task.DoesNotExist()


def get_tasks(user, tasks=None):
    tasks = tasks if tasks is not None else Task.objects.all()
    return tasks.filter(Q(created_by=user.pk) | Q(group_task__assignee=user.pk))


def get_group_tasks(user, group_tasks=None):
    group_tasks = group_tasks if group_tasks is not None else GroupTask.objects.all()
    return group_tasks.filter(group__in=[group.pk for group in user.groups.all()])


def is_task_created_by(user, task):
    created_user = get_created_user(task)
    return user == created_user


def am_i_assignee(user, task):
    return task in [group_task.task for group_task in GroupTask.objects.filter(assignee=user).all()]


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
    if is_task_created_by(user, task):
        return True
    group_task = convert_group_task(task)
    if group_task is None:
        return False
    return not (group_task.lock_level & GroupTask.DELETE_LOCK)


def is_completable_task(user, task):
    if is_task_created_by(user, task):
        return True
    group_task = convert_group_task(task)
    if group_task is None:
        return False
    return not (group_task.lock_level & GroupTask.COMPLETED_LOCK)


def is_assignable_task(user, task):
    group_task = convert_group_task(task)
    if group_task is None:
        return False
    if is_task_created_by(user, task):
        return not (group_task.assign_lock_level & GroupTask.ASSIGN_LOCK_CREATED_USER)
    if user == group_task.assignee:
        return not (group_task.assign_lock_level & GroupTask.ASSIGN_LOCK_ASSIGNEE)
    return not (group_task.assign_lock_level & GroupTask.ASSIGN_LOCK_MEMBERS)


def list_unchangeable_group_task_columns_by_member(group_task: GroupTask):
    bits_and_columns = {
        GroupTask.TITLE_LOCK: 'title',
        GroupTask.DETAIL_LOCK: 'detail',
        GroupTask.DUE_DATE_LOCK: 'due_date',
        GroupTask.STATUS_LOCK: 'status',
        GroupTask.TAG_LOCK: 'tag',
    }
    result = []
    for bit, column in bits_and_columns.items():
        if bit & group_task.lock_level:
            result.append(column)
    return result
