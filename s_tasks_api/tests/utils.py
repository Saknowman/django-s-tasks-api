from django.contrib.auth import get_user_model
from rest_framework import test
from rest_framework.exceptions import ValidationError

User = get_user_model()


class BaseApiTestCase(test.APITestCase):
    fixtures = ['test_users.json']


validation_error_status = ValidationError.status_code
