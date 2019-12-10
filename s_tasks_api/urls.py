from django.urls import path, include
from rest_framework import routers

from .views import TaskViewSet, TaskStatusViewSet, TaskTagViewSet

router = routers.DefaultRouter()
router.register(r'status', TaskStatusViewSet, 'status')
router.register(r'tags', TaskTagViewSet, 'tags')
router.register(r'', TaskViewSet, 'tasks')

app_name = 'tasks'
urlpatterns = [
    path(r'', include(router.urls)),
]
