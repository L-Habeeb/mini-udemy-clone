"""
URL mappings for the Course app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from courses import views


router = DefaultRouter()
router.register('course', views.CourseViewSet)
router.register('categories', views.CategoryViewSet)

app_name = 'course'

urlpatterns = [
    path('', include(router.urls)),
]
