from django.urls import reverse
from rest_framework import test


class AddTaskTestCase(test.APITestCase):
    fixtures = ['test_users.json', 'default_task_status_data.json']

    ADD_TASK_URL = reverse('task-list')
