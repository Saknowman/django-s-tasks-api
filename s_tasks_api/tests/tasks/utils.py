from django.contrib.auth.models import Group
from django.urls import reverse

from ..utils import BaseApiTestCase, User

LIST_TASK_URL = reverse('s-tasks:tasks-list')
ADD_TASK_URL = reverse('s-tasks:tasks-list')
DETAIL_TASK_URL_NAME = 's-tasks:tasks-detail'
COMPLETE_TASK_URL_NAME = 's-tasks:tasks-complete'
UN_COMPLETE_TASK_URL_NAME = 's-tasks:tasks-un-complete'
CREATE_GROUP_TASK_URL = reverse('s-tasks:tasks-create-group-task')
LIST_GROUP_TASK_URL = reverse('s-tasks:group-tasks-list')
DETAIL_GROUP_TASK_URL = 's-tasks:group-tasks-detail'
COMPLETE_GROUP_TASK_URL_NAME = 's-tasks:group-tasks-complete'
UN_COMPLETE_GROUP_TASK_URL_NAME = 's-tasks:group-tasks-un-complete'
REMOVE_TO_MY_TASK_URL_NAME = 's-tasks:group-tasks-remove-to-my-task'


def get_detail_task_url(pk):
    return reverse(DETAIL_TASK_URL_NAME, args=[pk])


def get_detail_group_task_url(pk):
    return reverse(DETAIL_GROUP_TASK_URL, args=[pk])


def get_complete_task_url(pk):
    return reverse(COMPLETE_TASK_URL_NAME, args=[pk])


def get_un_complete_task_url(pk):
    return reverse(UN_COMPLETE_TASK_URL_NAME, args=[pk])


def get_complete_group_task_url(pk):
    return reverse(COMPLETE_GROUP_TASK_URL_NAME, args=[pk])


def get_un_complete_group_task_url(pk):
    return reverse(UN_COMPLETE_GROUP_TASK_URL_NAME, args=[pk])


def get_remove_to_my_task_url(pk):
    return reverse(REMOVE_TO_MY_TASK_URL_NAME, args=[pk])


class BaseTaskTestCase(BaseApiTestCase):
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
        self.member_2 = User.objects.get(username='group1_member2')
        self.member_3 = User.objects.get(username='group1_member3')
        self.both_group_member = User.objects.get(username='group1_and_2_member')
        self.group_2_member = User.objects.get(username='group2_member1')
        self.group_1 = self.get_groups()[0]
        self.group_2 = self.get_groups()[1]
        self.client.force_login(self.member_1)

    def get_group_users_name(self, group_name):
        return self.groups_info[group_name]['users']

    def get_group_users(self, group_name):
        return User.objects.filter(username__in=self.get_group_users_name(group_name))

    def get_groups(self):
        return Group.objects.filter(name__in=self.groups_info.keys())
