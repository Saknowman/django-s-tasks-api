from rest_framework import status

from s_tasks_api.models import Task
from s_tasks_api.services.tasks import get_tasks
from .utils import BaseTaskTestCase, LIST_TASK_URL, get_detail_task_url


class AddTaskTestCase(BaseTaskTestCase):
    def test_list_tasks___without_authentication___404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.get(LIST_TASK_URL)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_tasks___without_authentication___404(self):
        # Arrange
        self.client.logout()
        task = Task.objects.all()[0]
        # Act
        response = self.client.get(get_detail_task_url(task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_list_tasks___there_are_some_users_tasks___get_tasks_which_created_by_user(self):
        # Arrange
        users = [self.user_1, self.user_2]
        for user in users:
            with self.subTest(user=user):
                self.client.force_login(user)
                expected_tasks = Task.objects.filter(created_by=user.pk).all()
                # Act
                response = self.client.get(LIST_TASK_URL)
                # Assert
                for index, expected_task in enumerate(expected_tasks):
                    self.assertEqual(expected_task.pk, response.data[index]['pk'])

    def test_detail_task___not_exists_pk___404(self):
        # Act
        response = self.client.get(get_detail_task_url(999))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_task___not_my_task___404(self):
        # Arrange
        not_my_task = get_tasks(self.user_2)[0]
        # Act
        response = self.client.get(get_detail_task_url(not_my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_task___my_task___200(self):
        # Arrange
        my_task = get_tasks(self.user_1)[0]
        # Act
        response = self.client.get(get_detail_task_url(my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
