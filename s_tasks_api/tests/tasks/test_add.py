from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status

from s_tasks_api.models import TaskStatus, Task, GroupTask
from s_tasks_api.tests.utils import validation_error_status, User
from ...settings import api_settings
from .utils import BaseTaskTestCase, ADD_TASK_URL, CREATE_GROUP_TASK_URL, LIST_GROUP_TASK_URL


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
        parameters = {
            'title': 'aaa', 'detail': 'task detail',
            'due_date': '2099-12-03', 'status': 2, 'tag': 1}
        # Act
        response = self.client.post(ADD_TASK_URL, parameters)
        # Assert
        self.assertTrue('pk' in response.data.keys(), response.data)
        task = Task.objects.get(pk=response.data['pk'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)
        self.assertEqual(self.member_1, task.created_by)
        for k, v in parameters.items():
            with self.subTest(k=k, v=v):
                if k is 'status' or k is 'tag':
                    self.assertEqual(v, task.__getattribute__(k).pk)
                    continue
                if k is 'due_date':
                    self.assertEqual(v, str(task.__getattribute__(k)))
                    continue
                self.assertEqual(v, task.__getattribute__(k))

    def test_add_task___set_value_wrong_data___validation_failed(self):
        # Arrange
        TaskStatus.objects.create(value='aaa')
        test_data_list = [
            {
                'parameters': {},
                'validation_errors': {'title': 'required'}
            },
            {
                'parameters': {'title': ''},
                'validation_errors': {'title': 'blank'}
            },
            {
                'parameters': {'title': ('a' * api_settings.TASK_MODEL['TITLE_MAX_LENGTH'] + 'a')},
                'validation_errors': {'title': 'max_length'}
            },
            {
                'parameters': {'title': 'aaa', 'due_date': '999'},
                'validation_errors': {'due_date': 'invalid'}
            },
            {
                'parameters': {'title': 'aaa', 'status': '999', 'tag': '999'},
                'validation_errors': {'status': 'does_not_exist', 'tag': 'does_not_exist'}
            },
        ]
        # SubTest
        for test_data in test_data_list:
            with self.subTest(parameters=test_data['parameters'], validation_errors=test_data['validation_errors']):
                # Act
                response = self.client.post(ADD_TASK_URL, test_data['parameters'])
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                for key, code in test_data['validation_errors'].items():
                    self.assertTrue(key in response.data.keys(), response.data)
                    self.assertEqual(code, response.data[key][0].code, response.data)

    def test_add_task___with_fewest_parameters___should_set_default_values(self):
        # Arrange
        expect_result = {
            'detail': api_settings.TASK_MODEL['DETAIL_DEFAULT'],
            'due_date': None,
            'status': TaskStatus.objects.get(pk=api_settings.TASK_MODEL['STATUS_DEFAULT_PK']),
            'tag': None,
            'created_date': timezone.now().date(),
            'completed': False,
            'completed_date': None
        }
        # Act
        response = self.client.post(ADD_TASK_URL, {'title': 'aaa'})
        # Assert
        self.assertTrue('pk' in response.data.keys())
        task = Task.objects.get(pk=response.data['pk'])
        for key, value in expect_result.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(value, task.__getattribute__(key))


class AddGroupTaskTestCase(BaseTaskTestCase):
    fixtures = ['test_group_users.json', 'default_task_status_data.json', 'test_task_tags_data.json',
                'test_tasks_data.json']

    def test_add_task___group_in_parameters___return_201_insert_at_db(self):
        # Arrange
        group_member = self.get_group_users('task_group_1').last()
        parameters = {"title": "group task 1", "group": self.group_1.pk, 'assignee': group_member.pk}
        # Act
        response = self.client.post(CREATE_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        group_task = GroupTask.objects.get(pk=response.data['pk'])
        self.assertEqual('group task 1', response.data['task']['title'])
        self.assertEqual(self.group_1.pk, response.data['group'], response.data)
        self.assertEqual(group_task.group, self.group_1)
        self.assertEqual(group_task.task.pk, response.data['task']['pk'])
        self.assertEqual(group_task.assignee, group_member)

    def test_add_task___assignee_is_not_group_member___return_404(self):
        # Arrange
        other_member = User.objects.exclude(groups__pk=self.group_1.pk).last()
        parameters = {"title": "group task 1", "group": self.group_1.pk, 'assignee': other_member.pk}
        # Act
        response = self.client.post(CREATE_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_task___user_is_not_in_group___return_404(self):
        # Arrange
        other_group = self.get_groups().exclude(pk=self.group_1.pk).first()
        group_member = self.get_group_users('task_group_1').last()
        parameters = {"title": "group task 1", "group": other_group.pk, 'assignee': group_member.pk}
        # Act
        response = self.client.post(CREATE_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_group_task___already_task_exists___return_201(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_1.pk).first()
        group_member = self.get_group_users('task_group_1').last()
        parameters = {"task_id": task.pk, "group": self.group_1.pk, 'assignee': group_member.pk}
        # Act
        response = self.client.post(LIST_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)
        self.assertEqual(self.group_1.pk, response.data['group'])
        self.assertEqual(task.pk, response.data['task']['pk'])
        self.assertEqual(response.data['assignee'], group_member.pk)

    def test_add_group_task___not_exists_task___return_404(self):
        # Arrange
        parameters = {'task_id': 999, 'group': self.group_1.pk}
        # Act
        response = self.client.post(LIST_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_task___not_users_group_in_parameter___return_404(self):
        # Arrange
        other_group = self.get_groups().exclude(pk=self.group_1.pk).first()
        parameters = {'title': 'group task 1', 'group': other_group.pk}
        # Act
        response = self.client.post(ADD_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    def test_add_group_task___not_users_task___return_404(self):
        # Arrange
        other_task = Task.objects.exclude(created_by=self.member_1.pk).first()
        parameters = {'task_id': other_task.pk, 'group': self.group_1.pk}
        # Act
        response = self.client.post(LIST_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_group_task___not_user_group_task___return_404(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_1.pk).first()
        other_group = Group.objects.exclude(pk=self.member_1.groups.first().pk).first()
        parameters = {'task_id': task.pk, 'group': other_group.pk}
        # Act
        response = self.client.post(LIST_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_group_task___assignee_is_not_group_member___return_404(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_1.pk).first()
        other_member = User.objects.exclude(groups__pk=self.group_1.pk).last()
        parameters = {'task_id': task.pk, 'group': self.group_1.pk, 'assignee': other_member.pk}
        # Act
        response = self.client.post(LIST_GROUP_TASK_URL, parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    def test_add_group_task___with_wrong_parameters___invalid_response(self):
        # Arrange
        test_data_list = [
            {
                'parameters': {},
                'validation_errors': {'task_id': 'required', 'group': 'required'}
            },
            {
                'parameters': {'task_id': '', 'group': ''},
                'validation_errors': {'task_id': 'null', 'group': 'null'}
            },
            {
                'parameters': {'lock_level': GroupTask.FULL_LOCK + 1,
                               'assign_lock_level': GroupTask.ASSIGN_FULL_LOCK + 1},
                'validation_errors': {'lock_level': 'max_value', 'assign_lock_level': 'max_value'}
            },
            {
                'parameters': {'lock_level': GroupTask.NON_LOCK - 1,
                               'assign_lock_level': GroupTask.ASSIGN_LOCK_NON - 1},
                'validation_errors': {'lock_level': 'min_value', 'assign_lock_level': 'min_value'}
            }
        ]
        # Sub Test
        for test_data in test_data_list:
            parameters = test_data['parameters']
            validation_errors = test_data['validation_errors']
            with self.subTest(parameters=parameters, validation_errors=validation_errors):
                # Act
                response = self.client.post(LIST_GROUP_TASK_URL, parameters)
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                for item, error_code in validation_errors.items():
                    self.assertTrue(item in response.data.keys(), "{item} is not in response data".format(item=item))
                    self.assertEqual(error_code, response.data[item][0].code, item + str(response.data[item]))
