from django.contrib.auth import get_user_model
from rest_framework import test

User = get_user_model()


class BaseApiTestCase(test.APITestCase):
    fixtures = ['test_users.json']
