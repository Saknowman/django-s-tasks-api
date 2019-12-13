from rest_framework import status

from s_tasks_api.models import Task, GroupTask
from s_tasks_api.services.tasks import get_tasks
from .utils import BaseTaskTestCase, LIST_TASK_URL, get_detail_task_url, \
    get_detail_group_task_url, LIST_GROUP_TASK_URL


class ReadTaskTestCase(BaseTaskTestCase):
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
        users = [self.member_1, self.member_2]
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
        not_my_task = get_tasks(self.member_2)[0]
        # Act
        response = self.client.get(get_detail_task_url(not_my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_task___my_task___200(self):
        # Arrange
        my_task = get_tasks(self.member_1)[0]
        # Act
        response = self.client.get(get_detail_task_url(my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class ReadGroupTaskTestCase(BaseTaskTestCase):
    def test_list_group_tasks___without_authentication___404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.get(LIST_GROUP_TASK_URL)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_group_task___without_authentication___404(self):
        # Arrange
        self.client.logout()
        group_task = GroupTask.objects.first()
        # Act
        response = self.client.get(get_detail_group_task_url(group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_list_group_tasks___with_authentication___200_list_only_my_group_tasks(self):
        # Arrange
        expected_group_tasks_pk = [group_task.pk for group_task in
                                   GroupTask.objects.filter(
                                       group__in=[group.pk for group in self.member_1.groups.all()]).all()]
        # Act
        response = self.client.get(LIST_GROUP_TASK_URL)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(expected_group_tasks_pk, [d['pk'] for d in response.data])

    def test_detail_group_task___my_group_task___200(self):
        # Arrange
        group_task = GroupTask.objects.filter(group=self.group_1.pk).first()
        # Act
        response = self.client.get(get_detail_group_task_url(group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(group_task.pk, response.data['pk'])

    def test_detail_group_task___no_my_group_tasks___404(self):
        # Arrange
        other_group_task = GroupTask.objects.exclude(group=self.group_1.pk).first()
        # Act
        response = self.client.get(get_detail_group_task_url(other_group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_group_task___not_exists_pk___404(self):
        # Act
        response = self.client.get(get_detail_group_task_url(999))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
