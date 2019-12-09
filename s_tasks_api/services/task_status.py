from s_tasks_api.models import TaskStatus
from s_tasks_api.settings import api_settings


def get_task_status_from_or_default(dictionary: dict):
    if 'status' not in dictionary.keys():
        return get_default_task_status()
    return get_default_task_status() if dictionary['status'] is None else dictionary['status']


def get_default_task_status():
    return TaskStatus.objects.get(pk=api_settings.TASK_MODEL['STATUS_DEFAULT_PK'])
