from django.db.models import Q
from rest_framework import status

from s_tasks_api.models import Task, GroupTask, TaskStatus, TaskTag
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
                expected_tasks = [task for task in Task.objects.filter(created_by=user.pk).all()]
                expected_tasks += [group_task.task for group_task in GroupTask.objects.filter(assignee=user.pk).all()]
                expected_tasks = set(expected_tasks)
                # Act
                response = self.client.get(LIST_TASK_URL)
                # Assert
                self.assertEqual(len(expected_tasks), len(response.data), response.data)
                for index, expected_task in enumerate(expected_tasks):
                    self.assertEqual(expected_task.pk, response.data[index]['pk'])

    def test_list_tasks___with_filter___filtered(self):
        # Arrange
        tasks = Task.objects.filter(Q(created_by=self.member_1) | Q(group_task__assignee=self.member_1))
        test_data_list = [
            {'conditions': {'title': 'filter_title'},
             'expect_result_tasks': tasks.filter(title__icontains='filter_title')},
            {'conditions': {'detail': 'filter_detail'},
             'expect_result_tasks': tasks.filter(detail__icontains='filter_detail')},
            {'conditions': {'title': 'filter_title', 'detail': 'filter_detail'},
             'expect_result_tasks': tasks.filter(title__icontains='filter_title', detail__icontains='filter_detail')},
            {'conditions': {'due_date': '2020-01-01'},
             'expect_result_tasks': tasks.filter(due_date__lte='2020-01-01')},
            {'conditions': {'completed': True},
             'expect_result_tasks': tasks.filter(completed=True)},
            {'conditions': {'completed': False},
             'expect_result_tasks': tasks.filter(completed=False)},
            {'conditions': {'status': TaskStatus.objects.first().pk},
             'expect_result_tasks': tasks.filter(status=TaskStatus.objects.first().pk)},
            {'conditions': {'status': TaskStatus.objects.last().pk},
             'expect_result_tasks': tasks.filter(status=TaskStatus.objects.last().pk)},
            {'conditions': {'tag': TaskTag.objects.first().pk},
             'expect_result_tasks': tasks.filter(tag=TaskTag.objects.first().pk)},
            {'conditions': {'tag': TaskTag.objects.last().pk},
             'expect_result_tasks': tasks.filter(tag=TaskTag.objects.last().pk)},

        ]
        # Sub Test
        for test_data in test_data_list:
            conditions = test_data['conditions']
            expect_result_tasks = test_data['expect_result_tasks'].all()
            with self.subTest(conditions=conditions, expect_result_tasks=expect_result_tasks):
                # Act
                response = self.client.get(LIST_TASK_URL, conditions)
                # Assert
                print(conditions)
                print(response.data)
                self.assertEqual(status.HTTP_200_OK, response.status_code)
                self.assertListEqual([task.pk for task in expect_result_tasks], [task['pk'] for task in response.data])

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
