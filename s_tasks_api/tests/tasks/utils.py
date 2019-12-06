from django.urls import reverse

from ..utils import BaseApiTestCase, User

ADD_TASK_URL = reverse('tasks:tasks-list')


class BaseTaskTestCase(BaseApiTestCase):
    fixtures = ['test_users.json', 'default_task_status_data.json', 'default_task_tags_data.json']

    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.get(is_superuser=True)
        self.user_1 = User.objects.get(pk=2)
        self.user_2 = User.objects.get(pk=3)
        self.client.force_login(self.user_1)
