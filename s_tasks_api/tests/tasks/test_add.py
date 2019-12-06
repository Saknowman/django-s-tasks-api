from django.urls import reverse
from rest_framework import test, status

from s_tasks_api.models import TaskStatus
from ...settings import api_settings
from .utils import BaseTaskTestCase, ADD_TASK_URL


class AddTaskTestCase(BaseTaskTestCase):
    def test_add_task___without_authentication___return_404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.post(ADD_TASK_URL, {})
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_task___with_authentication___return_201_insert_at_db(self):
        # Arrange
        parameters = {'title': 'aaa'}
        # Act
        response = self.client.post(ADD_TASK_URL, parameters)
        expect_default_task_status = TaskStatus.objects.get(pk=api_settings.TASK_MODEL['STATUS_DEFAULT_PK'])
        print(response.data)
        # Assert
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(expect_default_task_status.pk, response.data['status']['pk'])
