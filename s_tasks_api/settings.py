from django.conf import settings

APP_SETTING_ROUTE_NAME = 'S_TASKS_API'

DEFAULTS = {
    'TASK_TAG_MODEL': {
        'MAX_LENGTH': 20,
    },
    'TASK_STATUS_MODEL': {
        'MAX_LENGTH': 20,
    },
    'TASK_MODEL': {
        'TITLE_MAX_LENGTH': 100,
        'TITLE_DEFAULT': '',
        'DETAIL_DEFAULT': '',
        'STATUS_DEFAULT': 1,
    },
    'TASK_TAG_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        's_tasks_api.permissions.task_tags.OnlyAdminCanChange'
    ],
}


class APISettings:
    """
    A settings object, that allows API settings to be accessed as properties.
    Set default settings in your app settings.py like this:
        from app_utils.setting import APISettings
        api_settings = APISettings('TODO_API', DEFAULTS)
    For example:
        from todo_api.settings import api_settings
        print(api_settings.TASK_STATUS_CHOICES)
    """

    def __init__(self, setting_root_name, defaults):
        self._setting_root_name = setting_root_name
        self._defaults = defaults
        self._user_settings = getattr(settings, self._setting_root_name, {})

    def __getattr__(self, item):
        if item not in self._defaults:
            raise AttributeError("Invalid {} setting: {}".format(self._setting_root_name, item))

        try:
            return self._user_settings[item]
        except KeyError:
            return self._defaults[item]


api_settings = APISettings(APP_SETTING_ROUTE_NAME, DEFAULTS)
