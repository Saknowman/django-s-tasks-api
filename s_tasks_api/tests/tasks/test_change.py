from django.db.models import Q
from django.utils import timezone
from rest_framework import status

from s_tasks_api.models import Task, GroupTask, TaskStatus, TaskTag
from s_tasks_api.services.tasks import get_tasks, complete_task, un_complete_task
from s_tasks_api.settings import api_settings
from s_tasks_api.tests.utils import validation_error_status
from .utils import BaseTaskTestCase, get_detail_task_url, get_complete_task_url, get_un_complete_task_url, \
    get_detail_group_task_url, get_complete_group_task_url, get_un_complete_group_task_url


def _assert_task_is_not_changed_some_columns(test_case, task_in_db, response):
    test_case.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
    test_case.assertEqual(False, task_in_db.completed)
    test_case.assertEqual(None, task_in_db.completed_date)
    test_case.assertEqual(task_in_db.created_date, task_in_db.created_date)
    test_case.assertEqual(task_in_db.created_by, task_in_db.created_by)


class ChangeTaskTestCase(BaseTaskTestCase):
    def test_change_task___with_good_parameters___200_and_changed_task_detail(self):
        # Arrange
        parameters = {
            'title': 'changed', 'detail': 'changed detail',
            'due_date': '2100-10-10', 'status': 3, 'tag': 3}
        task = Task.objects.first()
        # Act
        response = self.client.put(get_detail_task_url(task.pk), parameters)
        task_in_db = Task.objects.get(pk=task.pk)
        # Assert
        self._assert_success_change_parameters_correctly(parameters, response, task_in_db)

    def test_change_task___i_assign_with_good_parameters___200_and_changed_task_detail(self):
        # Arrange
        parameters = {
            'title': 'changed', 'detail': 'changed detail',
            'due_date': '2100-10-10', 'status': 3, 'tag': 3}
        task = Task.objects.filter(created_by=self.member_2, group_task__assignee=self.member_1).first()
        # Act
        response = self.client.put(get_detail_task_url(task.pk), parameters)
        task_in_db = Task.objects.get(pk=task.pk)
        # Assert
        self._assert_success_change_parameters_correctly(parameters, response, task_in_db)

    def test_change_task___i_assign_with_good_parameters_but_is_locked___403(self):
        # Arrange
        parameters = {
            'title': 'changed', 'detail': 'changed detail',
            'due_date': '2100-10-10', 'status': 3, 'tag': 3}
        task = Task.objects.filter(created_by=self.member_2, group_task__assignee=self.member_1).first()
        task.group_task.lock_level = GroupTask.FULL_LOCK
        task.group_task.save()
        # Act
        response = self.client.put(get_detail_task_url(task.pk), parameters)
        # Assert
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        for column in parameters.keys():
            self.assertTrue(column in response.data['detail'], column)

    def _assert_success_change_parameters_correctly(self, parameters, response, task_in_db):
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
        task = Task.objects.first()
        # Act
        response = self.client.patch(get_detail_task_url(task.pk), parameters)
        task_in_db = Task.objects.get(pk=task.pk)
        # Assert
        _assert_task_is_not_changed_some_columns(self, task_in_db, response)

    def test_complete_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        task = Task.objects.first()
        un_complete_task(self.member_1, task.pk)
        # Act
        response = self.client.patch(get_complete_task_url(task.pk))
        task = Task.objects.get(pk=task.pk)
        # Assert
        self._assert_success_complete_task(response, task)

    def _assert_success_complete_task(self, response, task):
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(True, task.completed)
        self.assertEqual(timezone.now().date(), task.completed_date)

    def test_complete_task___i_assign_task___200_and_task_is_completed(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_2, group_task__assignee=self.member_1).first()
        un_complete_task(self.member_1, task.pk)
        # Act
        response = self.client.patch(get_complete_task_url(task.pk))
        task = Task.objects.get(pk=task.pk)
        # Assert
        self._assert_success_complete_task(response, task)

    def test_un_complete_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        task = Task.objects.first()
        complete_task(self.member_1, task.pk)
        # Act
        response = self.client.patch(get_un_complete_task_url(task.pk))
        task = Task.objects.get(pk=task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(False, task.completed)
        self.assertEqual(None, task.completed_date)

    def test_complete_task___is_group_task_and_locked___403(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_2, group_task__assignee=self.member_1).first()
        task.group_task.lock_level = GroupTask.COMPLETED_LOCK
        task.group_task.save()
        # Act
        response = self.client.patch(get_complete_task_url(task.pk))
        # Assert
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, response.data)

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
                task = Task.objects.first()
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
        task = Task.objects.first()
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
        not_my_task = get_tasks(self.member_2)[0]
        # Act
        response = self.client.put(get_detail_task_url(not_my_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class ReadGroupTaskTestCase(BaseTaskTestCase):

    def test_change_group_task___without_authentication___404(self):
        # Arrange
        self.client.logout()
        group_task = GroupTask.objects.first()
        # Act
        response = self.client.patch(get_detail_group_task_url(group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_group_task___not_my_group_task___404(self):
        # Arrange
        other_group_task = GroupTask.objects.exclude(group=self.group_1.pk).first()
        # Act
        response = self.client.patch(get_detail_group_task_url(other_group_task.pk))
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_group_task___other_member_task_is_some_locked___cannot_change_locked_column(self):
        # Arrange
        other_member_group_task = GroupTask.objects.filter(task__created_by=self.member_2.pk).first()
        parameters = {'title': 'changed', 'detail': 'changed', 'due_date': '2055-05-05',
                      'status': TaskStatus.objects.first().pk, 'tag': TaskTag.objects.first().pk}
        test_data_list = [
            {'lock_level': GroupTask.TITLE_LOCK, 'unchangeable_columns': ['title']},
            {'lock_level': GroupTask.DETAIL_LOCK, 'unchangeable_columns': ['detail']},
            {'lock_level': GroupTask.DUE_DATE_LOCK, 'unchangeable_columns': ['due_date']},
            {'lock_level': GroupTask.STATUS_LOCK, 'unchangeable_columns': ['status']},
            {'lock_level': GroupTask.TAG_LOCK, 'unchangeable_columns': ['tag']},
            {'lock_level': GroupTask.TITLE_LOCK | GroupTask.DETAIL_LOCK, 'unchangeable_columns': ['title', 'detail']},
            {'lock_level': GroupTask.TITLE_LOCK | GroupTask.DETAIL_LOCK | GroupTask.STATUS_LOCK,
             'unchangeable_columns': ['title', 'detail', 'status']},
            {'lock_level': GroupTask.FULL_LOCK,
             'unchangeable_columns': ['title', 'detail', 'due_date', 'status', 'tag']},
        ]
        # SubTest
        for test_data in test_data_list:
            lock_level = test_data['lock_level']
            unchangeable_columns = test_data['unchangeable_columns']
            other_member_group_task.lock_level = lock_level
            other_member_group_task.save()
            with self.subTest(lock_level=lock_level, unchangeable_columns=unchangeable_columns):
                # Act
                response = self.client.patch(get_detail_group_task_url(other_member_group_task.pk), parameters)
                # Assert
                self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, response.data)
                for column in unchangeable_columns:
                    self.assertTrue(column in response.data['detail'], column + ' is not in ' + response.data['detail'])

    def test_complete_group_task___with_lock___403(self):
        # Arrange
        group_task = GroupTask.objects.filter(task__created_by=self.member_2).first()
        group_task.lock_level = GroupTask.COMPLETED_LOCK
        group_task.save()
        # Act
        response = self.client.patch(get_complete_group_task_url(group_task.pk), {'title': 'locked'})
        # Assert
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_un_complete_group_task___with_lock___403(self):
        # Arrange
        group_task = GroupTask.objects.filter(task__created_by=self.member_2).first()
        group_task.lock_level = GroupTask.COMPLETED_LOCK
        group_task.save()
        # Act
        response = self.client.patch(get_un_complete_group_task_url(group_task.pk), {'title': 'locked'})
        # Assert
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_change_assignee___assign_to_not_group_user___404(self):
        # Arrange
        group_task = GroupTask.objects.filter(group=self.group_1.pk).first()
        parameters = {'assignee': self.group_2_member.pk}
        # Act
        response = self.client.patch(get_detail_group_task_url(group_task.pk), parameters)
        # Assert
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    def test_change_assignee___some_assign_locks___200_or_403(self):
        # Arrange
        test_data_list = [
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS, 'user': self.member_3,
             'assignee': None, 'status': status.HTTP_403_FORBIDDEN},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS, 'user': self.member_2,
             'assignee': self.member_2, 'status': status.HTTP_200_OK},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS, 'user': self.member_1,
             'assignee': self.member_2, 'status': status.HTTP_200_OK},

            {'assign_lock_level': GroupTask.ASSIGN_LOCK_ASSIGNEE, 'user': self.member_3,
             'assignee': None, 'status': status.HTTP_200_OK},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_ASSIGNEE, 'user': self.member_2,
             'assignee': self.member_2, 'status': status.HTTP_403_FORBIDDEN},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_ASSIGNEE, 'user': self.member_1,
             'assignee': self.member_2, 'status': status.HTTP_200_OK},

            {'assign_lock_level': GroupTask.ASSIGN_LOCK_CREATED_USER, 'user': self.member_3,
             'assignee': None, 'status': status.HTTP_200_OK},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_CREATED_USER, 'user': self.member_2,
             'assignee': self.member_2, 'status': status.HTTP_200_OK},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_CREATED_USER, 'user': self.member_1,
             'assignee': self.member_2, 'status': status.HTTP_403_FORBIDDEN},

            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS | GroupTask.ASSIGN_LOCK_ASSIGNEE,
             'user': self.member_3, 'assignee': None, 'status': status.HTTP_403_FORBIDDEN},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS | GroupTask.ASSIGN_LOCK_ASSIGNEE,
             'user': self.member_2, 'assignee': self.member_2, 'status': status.HTTP_403_FORBIDDEN},
            {'assign_lock_level': GroupTask.ASSIGN_LOCK_MEMBERS | GroupTask.ASSIGN_LOCK_ASSIGNEE,
             'user': self.member_1, 'assignee': self.member_2, 'status': status.HTTP_200_OK},
        ]
        group_task = GroupTask.objects.filter(task__created_by=self.member_1).first()
        # SubTest
        for test_data in test_data_list:
            assign_lock_level = test_data['assign_lock_level']
            user = test_data['user']
            assignee = test_data['assignee']
            expected_status = test_data['status']
            with self.subTest(assign_lock_level=assign_lock_level, user=user, assignee=assignee,
                              expected_status=expected_status):
                group_task.assign_lock_level = assign_lock_level
                group_task.assignee = assignee
                group_task.save()
                self.client.force_login(user)
                # Act
                response = self.client.patch(get_detail_group_task_url(group_task.pk),
                                             {'assignee': self.both_group_member.pk})
                # Assert
                self.assertEqual(expected_status, response.status_code, response.data)

    def test_complete_group_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        group_task = GroupTask.objects.filter(task__created_by=self.member_2).first()
        # Act
        response = self.client.patch(get_complete_group_task_url(group_task.pk))
        group_task = GroupTask.objects.get(pk=group_task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(True, group_task.task.completed)
        self.assertEqual(timezone.now().date(), group_task.task.completed_date)

    def test_un_complete_group_task___target_is_not_completed_task___200_and_task_is_completed(self):
        # Arrange
        group_task = GroupTask.objects.filter(task__created_by=self.member_2).first()
        complete_task(self.member_1, group_task.task.pk)
        # Act
        response = self.client.patch(get_un_complete_group_task_url(group_task.pk))
        group_task = GroupTask.objects.get(pk=group_task.pk)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(False, group_task.task.completed)
        self.assertEqual(None, group_task.task.completed_date)

    def test_change_group_task___other_member_group_task_without_lock___200_task_info_is_changed(self):
        # Arrange
        other_member_group_task = GroupTask.objects.filter(task__created_by=self.member_2.pk).first()
        other_member_group_task.lock_level = GroupTask.NON_LOCK
        other_member_group_task.save()
        parameters = {'title': 'changed', 'detail': 'changed', 'due_date': '2055-05-05',
                      'status': TaskStatus.objects.first().pk, 'tag': TaskTag.objects.first().pk,
                      'assignee': self.member_2.pk, 'lock_level': GroupTask.FULL_LOCK,
                      'assign_lock_level': GroupTask.ASSIGN_FULL_LOCK}
        # Act
        response = self.client.patch(get_detail_group_task_url(other_member_group_task.pk), parameters)
        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        for column, expected_value in parameters.items():
            if column in response.data['task'].keys():
                self.assertEqual(expected_value, response.data['task'][column], response.data)
                continue
            self.assertEqual(expected_value, response.data[column], response.data)

    def test_change_group_task___parameters_not_changeable___200_and_not_changed(self):
        # Arrange
        task = Task.objects.filter(created_by=self.member_1.pk).last()
        other_group = self.member_1.groups.last()
        parameters = {
            'task_id': task.pk, 'group': other_group.pk,
            'completed': True, 'completed_date': '2010-10-11',
            'created_date': '2010-10-10', 'created_by': 3
        }
        other_member_group_task = GroupTask.objects.filter(task__created_by=self.member_2.pk).first()
        other_member_group_task.lock_level = GroupTask.NON_LOCK
        other_member_group_task.save()
        # Act
        response = self.client.patch(get_detail_group_task_url(other_member_group_task.pk), parameters)
        group_task_in_db = GroupTask.objects.get(pk=other_member_group_task.pk)
        # Assert
        self.assertNotEqual(task.pk, response.data['task']['pk'])
        self.assertNotEqual(other_group.pk, response.data['group'])
        _assert_task_is_not_changed_some_columns(self, group_task_in_db.task, response)

    def test_change_group_task___set_value_wrong_data___validation_failed(self):
        # Arrange
        test_data_list = [
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
        # SubTest
        for test_data in test_data_list:
            with self.subTest(parameters=test_data['parameters'], validation_errors=test_data['validation_errors']):
                group_task = GroupTask.objects.filter(group=self.group_1.pk).first()
                # Act
                response = self.client.put(get_detail_group_task_url(group_task.pk), test_data['parameters'])
                # Assert
                self.assertEqual(validation_error_status, response.status_code, response.data)
                self.assertEqual(len(test_data['validation_errors']), len(response.data))
                for key, code in test_data['validation_errors'].items():
                    self.assertTrue(key in response.data.keys(), response.data)
                    self.assertEqual(code, response.data[key][0].code, response.data)
