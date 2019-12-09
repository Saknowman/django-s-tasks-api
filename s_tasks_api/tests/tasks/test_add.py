from django.urls import reverse
from django.utils import timezone
from rest_framework import test, status

from s_tasks_api.models import TaskStatus, Task
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
        parameters = {
            'title': 'aaa', 'detail': 'task detail',
            'due_date': '2099-12-03', 'status': 2, 'tag': 1}
        # Act
        response = self.client.post(ADD_TASK_URL, parameters)
        # Assert
        self.assertTrue('pk' in response.data.keys())
        task = Task.objects.get(pk=response.data['pk'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)
        self.assertEqual(self.user_1, task.created_by)
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
                'parameters': {'title': 'aaa', 'due_date': '999', 'completed_date': 'aaa', 'completed': 'aa'},
                'validation_errors': {'due_date': 'invalid', 'completed_date': 'invalid', 'completed': 'invalid'}
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
                self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
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
