from django.urls import reverse

from ..utils import BaseApiTestCase, User

LIST_TASK_URL = reverse('tasks:tasks-list')
ADD_TASK_URL = reverse('tasks:tasks-list')
DETAIL_TASK_URL_NAME = 'tasks:tasks-detail'
COMPLETE_TASK_URL_NAME = 'tasks:tasks-complete'
UN_COMPLETE_TASK_URL_NAME = 'tasks:tasks-un-complete'


def get_detail_task_url(pk):
    return reverse(DETAIL_TASK_URL_NAME, args=[pk])


def get_complete_task_url(pk):
    return reverse(COMPLETE_TASK_URL_NAME, args=[pk])


def get_un_complete_task_url(pk):
    return reverse(UN_COMPLETE_TASK_URL_NAME, args=[pk])


class BaseTaskTestCase(BaseApiTestCase):
    fixtures = ['test_users.json', 'default_task_status_data.json', 'test_task_tags_data.json', 'test_tasks_data.json']

    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.get(is_superuser=True)
        self.user_1 = User.objects.get(pk=2)
        self.user_2 = User.objects.get(pk=3)
        self.client.force_login(self.user_1)
