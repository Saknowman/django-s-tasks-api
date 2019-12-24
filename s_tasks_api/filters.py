from django_filters import rest_framework as filters


class TaskFilterSet(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='contains')
    detail = filters.CharFilter(field_name='detail', lookup_expr='contains')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    completed = filters.BooleanFilter(field_name='completed')
    status = filters.NumberFilter(field_name='status')
    tag = filters.NumberFilter(field_name='tag')


class GroupTaskFilterSet(filters.FilterSet):
    title = filters.CharFilter(field_name='task__title', lookup_expr='contains')
    detail = filters.CharFilter(field_name='task__detail', lookup_expr='contains')
    due_date = filters.DateFilter(field_name='task__due_date', lookup_expr='lte')
    completed = filters.BooleanFilter(field_name='task__completed')
    status = filters.NumberFilter(field_name='task__status')
    tag = filters.NumberFilter(field_name='task__tag')
    created_by = filters.NumberFilter(field_name='task__created_by')
    assignee = filters.NumberFilter(field_name='assignee')
    group = filters.NumberFilter(field_name='group')
