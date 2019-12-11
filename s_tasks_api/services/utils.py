from django.contrib.auth import get_user_model
from django.http import QueryDict

User = get_user_model()


def add_items_at_query_dict(query_dict, items):
    dictionary = query_dict.dict()
    for key, value in items.items():
        dictionary[key] = value
    result = QueryDict('', mutable=True)
    result.update(dictionary)
    return result


def is_in_same_group(user, other):
    other_groups = other.groups.all()
    for group in user.groups.all():
        if group in other_groups:
            return True
    return False
