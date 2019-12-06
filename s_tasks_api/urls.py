from django.urls import path, include
from rest_framework import routers

from .views import TaskStatusViewSet, TaskTagViewSet


router = routers.DefaultRouter()
router.register(r'status', TaskStatusViewSet, 'status')
router.register(r'tags', TaskTagViewSet, 'tags')

app_name = 'tasks'
urlpatterns = [
    path(r'', include(router.urls))
]