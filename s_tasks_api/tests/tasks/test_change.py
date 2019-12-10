from django.utils import timezone
from rest_framework import status

from s_tasks_api.models import Task
from s_tasks_api.services.tasks import get_tasks, complete_task
from s_tasks_api.settings import api_settings
from s_tasks_api.tests.utils import validation_error_status
from .utils import BaseTaskTestCase, get_detail_task_url, get_complete_task_url, get_un_complete_task_url


class ChangeTaskTestCase(BaseTaskTestCase):
    def test_change_task___with_good_parameters___200_and_changed_task_detail(self):
        # Arrange
        parameters = {
            'title': 'changed', 'detail': 'changed detail',
            'due_date': '2100-10-10', 'status': 3, 'tag': 3}
        task = Task.objects.all()[0]
        # Act
        response = self.client.put(get_detail_task_url(task.pk), parameters)
        task_in_db = Task.objects.get(pk=task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        for key, value in parameters.items():
            with self.subTest(key=key, value=value):
                if key is 'status' or key is 'tag':
                    self.assertEqual(value, task_in_db.__getattribute__(key).pk)
                    continue
                if key is 'due_date':
                    self.assertEqual(value, str(task_in_db.__getattribute__(key)))
                    continue
                self.assertEqual(value, task_in_db.__getattribute__(key))

    def test_change_task___parameters_not_changeable___200_and_not_changed(self):
        # Arrange
        parameters = {
            'completed': True, 'completed_date': '2010-10-11',
            'created_date': '2010-10-10', 'created_by': 3
        }
        task = Task.objects.all()[0]
        # Act
        response = self.client.patch(get_detail_task_url(task.pk), parameters)
        task_in_db = Task.objects.get(pk=task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(False, task_in_db.completed)
        self.assertEqual(None, task_in_db.completed_date)
        self.assertEqual(task.created_date, task_in_db.created_date)
        self.assertEqual(task.created_by, task_in_db.created_by)

    def test_complete_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        task = Task.objects.all()[0]
        # Act
        response = self.client.patch(get_complete_task_url(task.pk))
        task = Task.objects.get(pk=task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(True, task.completed)
        self.assertEqual(timezone.now().date(), task.completed_date)

    def test_un_complete_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        task = Task.objects.all()[0]
        complete_task(self.user_1, task.pk)
        # Act
        response = self.client.patch(get_un_complete_task_url(task.pk))
        task = Task.objects.get(pk=task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(False, task.completed)
        self.assertEqual(None, task.completed_date)

    def test_change_task___set_value_wrong_data___validation_failed(self):
        # Arrange
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
                task = Task.objects.all()[0]
                # Act
                response = self.client.put(get_detail_task_url(task.pk), test_data['parameters'])
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                for key, code in test_data['validation_errors'].items():
                    self.assertTrue(key in response.data.keys(), response.data)
                    self.assertEqual(code, response.data[key][0].code, response.data)

    def test_change_task___without_authentication___404(self):
        # Arrange
        self.client.logout()
        task = Task.objects.all()[0]
        # Act
        response = self.client.put(get_detail_task_url(task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_task___not_exists_pk___404(self):
        # Act
        response = self.client.put(get_detail_task_url(999))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_task___not_my_task___404(self):
        # Arrange
        not_my_task = get_tasks(self.user_2)[0]
        # Act
        response = self.client.put(get_detail_task_url(not_my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
