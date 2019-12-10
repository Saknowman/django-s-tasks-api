from django.utils import timezone
from rest_framework import status

from s_tasks_api.models import Task
from s_tasks_api.services.tasks import get_tasks
from .utils import BaseTaskTestCase, get_detail_task_url


class DeleteTaskTestCase(BaseTaskTestCase):
    def test_delete_task___my_task___203_and_deleted(self):
        # Arrange
        task = Task.objects.all()[0]
        # Act
        response = self.client.delete(get_detail_task_url(task.pk))
        # Assert
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_task___without_authentication___404(self):
        # Arrange
        self.client.logout()
        task = Task.objects.all()[0]
        # Act
        response = self.client.delete(get_detail_task_url(task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_task___not_exists_pk___404(self):
        # Act
        response = self.client.delete(get_detail_task_url(999))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_task___not_my_task___404(self):
        # Arrange
        not_my_task = get_tasks(self.user_2)[0]
        # Act
        response = self.client.delete(get_detail_task_url(not_my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)