from django.urls import path, include
from rest_framework import routers

from .views import TaskViewSet, TaskStatusViewSet, TaskTagViewSet, GroupTaskViewSet

router = routers.DefaultRouter()
router.register(r'status', TaskStatusViewSet, 'status')
router.register(r'tags', TaskTagViewSet, 'tags')
router.register(r'group', GroupTaskViewSet, 'group-tasks')
router.register(r'', TaskViewSet, 'tasks')
router.routes.append(routers.DynamicRoute(
    url=r'^{prefix}/{url_path}$',
    name='{basename}-{url_name}',
    detail=False,
    initkwargs={}
))

app_name = 'tasks'
urlpatterns = [
    path(r'', include(router.urls)),
]
