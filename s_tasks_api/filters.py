from django_filters import rest_framework as filters
from .models import Task, GroupTask


class TaskFilterSet(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='contains')
    detail = filters.CharFilter(field_name='detail', lookup_expr='contains')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    completed = filters.BooleanFilter(field_name='completed')
    status = filters.NumberFilter(field_name='status')
    tag = filters.NumberFilter(field_name='tag')
