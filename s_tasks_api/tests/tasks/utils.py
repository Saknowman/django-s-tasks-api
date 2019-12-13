from django.contrib.auth.models import Group
from django.urls import reverse

from ..utils import BaseApiTestCase, User

LIST_TASK_URL = reverse('tasks:tasks-list')
ADD_TASK_URL = reverse('tasks:tasks-list')
CREATE_GROUP_TASK_URL = reverse('tasks:tasks-create-group-task')
DETAIL_TASK_URL_NAME = 'tasks:tasks-detail'
COMPLETE_TASK_URL_NAME = 'tasks:tasks-complete'
UN_COMPLETE_TASK_URL_NAME = 'tasks:tasks-un-complete'
LIST_GROUP_TASK_URL = reverse('tasks:group-tasks-list')
DETAIL_GROUP_TASK_URL = 'tasks:group-tasks-detail'


def get_detail_task_url(pk):
    return reverse(DETAIL_TASK_URL_NAME, args=[pk])


def get_detail_group_task_url(pk):
    return reverse(DETAIL_GROUP_TASK_URL, args=[pk])


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


class BaseGroupTaskTestCase(BaseApiTestCase):
    fixtures = ['test_group_users.json', 'default_task_status_data.json', 'test_task_tags_data.json',
                'test_group_tasks_data.json']

    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.get(is_superuser=True)
        self.groups_info = {
            'task_group_1': {
                'users': [
                    'group1_member1', 'group1_member2', 'group1_member3', 'group1_and_2_member'
                ]
            },
            'task_group_2': {
                'users': [
                    'group2_member1', 'group2_member2', 'group1_and_2_member'
                ]
            }
        }
        self.member_1 = User.objects.get(username='group1_member1')
        self.group_1 = self.get_groups()[0]
        self.client.force_login(self.member_1)

    def get_group_users_name(self, group_name):
        return self.groups_info[group_name]['users']

    def get_group_users(self, group_name):
        return User.objects.filter(username__in=self.get_group_users_name(group_name))

    def get_groups(self):
        return Group.objects.filter(name__in=self.groups_info.keys())
