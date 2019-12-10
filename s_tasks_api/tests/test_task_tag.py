from django.urls import reverse
from rest_framework import status

from s_tasks_api.models import TaskTag
from .utils import BaseApiTestCase, User, validation_error_status
from ..settings import api_settings

LIST_TASK_TAG_URL = reverse('tasks:tags-list')


def detail_task_tag_url_by(pk):
    return reverse('tasks:tags-detail', args=[pk])


class BaseTaskTagTestCase(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.get(is_superuser=True)
        self.user_1 = User.objects.get(pk=2)
        self.client.force_login(self.user_1)


class AddTaskTagTestCase(BaseTaskTagTestCase):
    def test_add_task_tag___with_out_authentication___return_404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.post(LIST_TASK_TAG_URL, {})
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    def test_add_task_tag___with_authentication___return_201_and_inserted_at_db(self):
        # Act
        response = self.client.post(LIST_TASK_TAG_URL, {'value': 'aaa'})
        tags = TaskTag.objects.all()
        # Assert
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)
        self.assertEqual('aaa', response.data['value'])
        self.assertEqual(1, len(tags))
        self.assertEqual(response.data['pk'], tags[0].pk)
        self.assertEqual(response.data['value'], tags[0].value)

    def test_add_task_tag___set_value_wrong_data___validation_failed(self):
        # Arrange
        TaskTag.objects.create(value='aaa')
        parameters_list = [
            {
                'parameters': {'value': ('a' * api_settings.TASK_TAG_MODEL['MAX_LENGTH'] + 'a')},
                'validation_code': 'max_length'
            },
            {
                'parameters': {'value': ''},
                'validation_code': 'blank'
            },
            {
                'parameters': {'value': 'aaa'},
                'validation_code': 'unique'
            }
        ]
        # SubTest
        for parameters in parameters_list:
            with self.subTest(parameters=parameters['parameters'], validation_code=parameters['validation_code']):
                # Act
                response = self.client.post(LIST_TASK_TAG_URL, parameters['parameters'])
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                self.assertTrue('value' in response.data.keys())
                self.assertEqual(parameters['validation_code'], response.data['value'][0].code)


class ReadTaskTagTestCase(BaseTaskTagTestCase):
    fixtures = ['test_users.json', 'test_task_tags_data.json']

    def test_read_task_tag_list___without_authentication___return_404(self):
        # Arrange
        self.client.logout()
        # Act
        response = self.client.get(LIST_TASK_TAG_URL)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_read_task_tag_list___with_authentication___return_200_and_get_all_task_tags(self):
        # Arrange
        all_tags = TaskTag.objects.all()
        # Act
        response = self.client.get(LIST_TASK_TAG_URL)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(all_tags), len(response.data), response.data)
        for i in range(len(all_tags)):
            self.assertEqual(all_tags[i].pk, response.data[i]['pk'])
            self.assertEqual(all_tags[i].value, response.data[i]['value'])

    def test_read_task_tag_detail___with_authentication___return_200_get_target_task_tag(self):
        # Arrange
        all_tags = TaskTag.objects.all()
        # SubTest
        for tag in all_tags:
            with self.subTest(tag=tag):
                # Act
                response = self.client.get(detail_task_tag_url_by(tag.pk))
                # Assert
                self.assertEqual(tag.pk, response.data['pk'], response.data)
                self.assertEqual(tag.value, response.data['value'], response.data)

    def test_read_task_tag_detail___not_exists_pk___return_404(self):
        # Act
        response = self.client.get(detail_task_tag_url_by(111))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class ChangeTaskTagTestCase(BaseTaskTagTestCase):
    fixtures = ['test_users.json', 'test_task_tags_data.json']

    def test_change_task_tag___some_users_login___only_admin_user_can_change(self):
        # Arrange
        tag_pk = 1
        test_data = [
            {'user': self.admin_user, 'status_code': status.HTTP_200_OK, 'tag_value': 'changed'},
            {'user': self.user_1, 'status_code': status.HTTP_404_NOT_FOUND, 'tag_value': 'not_changed'},
        ]
        # SubTest
        for test_d in test_data:
            tag = TaskTag.objects.get(pk=tag_pk)
            tag.value = 'not_changed'
            tag.save()
            self.client.force_login(test_d['user'])
            with self.subTest(test_d=test_d):
                # Act
                response = self.client.put(detail_task_tag_url_by(tag_pk), {'value': 'changed'})
                # Assert
                self.assertEqual(test_d['status_code'], response.status_code)
                self.assertEqual(test_d['tag_value'], TaskTag.objects.get(pk=tag_pk).value)

    def test_change_task_tag___set_value_wrong_data___validation_failed(self):
        # Arrange
        self.client.force_login(self.admin_user)
        tag_pk = 1
        TaskTag.objects.create(value='aaa')
        parameters_list = [
            {
                'parameters': {'value': ('a' * api_settings.TASK_TAG_MODEL['MAX_LENGTH'] + 'a')},
                'validation_code': 'max_length'
            },
            {
                'parameters': {'value': ''},
                'validation_code': 'blank'
            },
            {
                'parameters': {'value': 'aaa'},
                'validation_code': 'unique'
            }
        ]
        # SubTest
        for parameters in parameters_list:
            with self.subTest(parameters=parameters['parameters'], validation_code=parameters['validation_code']):
                # Act
                response = self.client.put(detail_task_tag_url_by(tag_pk), parameters['parameters'])
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                self.assertTrue('value' in response.data.keys())
                self.assertEqual(parameters['validation_code'], response.data['value'][0].code)


class DeleteTaskTagTestCase(BaseTaskTagTestCase):
    fixtures = ['test_users.json', 'test_task_tags_data.json']

    def test_delete_task_tag___some_users_login___only_admin_user_can_delete(self):
        # Arrange
        tag_pk = 1
        test_data = [
            {'user': self.admin_user, 'status_code': status.HTTP_204_NO_CONTENT},
            {'user': self.user_1, 'status_code': status.HTTP_404_NOT_FOUND},
        ]
        # SubTest
        for test_d in test_data:
            self.client.force_login(test_d['user'])
            with self.subTest(test_d=test_d):
                # Act
                response = self.client.delete(detail_task_tag_url_by(tag_pk))
                # Assert
                self.assertEqual(test_d['status_code'], response.status_code)
                self.assertFalse(TaskTag.objects.filter(pk=tag_pk).exists())
