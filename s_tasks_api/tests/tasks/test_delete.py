from rest_framework import status

from s_tasks_api.models import Task, GroupTask
from s_tasks_api.services.tasks import get_tasks
from .utils import BaseTaskTestCase, get_detail_task_url, BaseGroupTaskTestCase, get_detail_group_task_url


class DeleteTaskTestCase(BaseTaskTestCase):
    def test_delete_task___my_task___204_and_deleted(self):
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


class DeleteGroupTaskTestCase(BaseGroupTaskTestCase):
    def test_delete_group_task___without_authentication___404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.delete(get_detail_group_task_url(self.group_1.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_group_task___not_exists___404(self):
        # Act
        response = self.client.delete(get_detail_group_task_url(999))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_group_task___not_my_group_task___404(self):
        # Arrange
        other_group_task = GroupTask.objects.exclude(group=self.group_1.pk).first()
        # Act
        response = self.client.delete(get_detail_group_task_url(other_group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    def test_delete_group_task___group_task_is_delete_locked_and_not_my_task___403(self):
        # Arrange
        other_member_task = GroupTask.objects.filter(task__created_by=self.member_2.pk).first()
        other_member_task.lock_level = GroupTask.DELETE_LOCK
        other_member_task.save()
        # Act
        response = self.client.delete(get_detail_group_task_url(other_member_task.pk))
        # Assert
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertTrue(GroupTask.objects.filter(pk=other_member_task.pk).exists())
        self.assertTrue(Task.objects.filter(pk=other_member_task.task.pk).exists())

    def test_delete_group_task___group_task_is_delete_locked_and_my_task___403(self):
        # Arrange
        my_group_task = GroupTask.objects.filter(task__created_by=self.member_1.pk).first()
        my_group_task.lock_level = GroupTask.DELETE_LOCK
        my_group_task.save()
        self._assert_status_204_and_tasks_not_exists(my_group_task)

    def test_delete_group_task___my_task___203(self):
        # Arrange
        group_task = GroupTask.objects.filter(task__created_by=self.member_1.pk).first()
        self._assert_status_204_and_tasks_not_exists(group_task)

    def _assert_status_204_and_tasks_not_exists(self, my_group_task):
        my_task = my_group_task.task
        # Act
        response = self.client.delete(get_detail_group_task_url(my_group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(GroupTask.objects.filter(pk=my_group_task.pk).exists())
        self.assertFalse(Task.objects.filter(pk=my_task.pk).exists())
