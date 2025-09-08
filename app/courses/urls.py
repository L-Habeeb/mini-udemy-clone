"""
URL mappings for the Course app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from courses import views
from curriculum import views as course_content_views


router = DefaultRouter()
router.register('course', views.CourseViewSet)
router.register('categories', views.CategoryViewSet)


app_name = 'course'

urlpatterns = [
    path('', include(router.urls)),
    path('curriculum/<int:course_id>/',
         course_content_views.CurriculumViews.as_view(),
         name='curriculum-detail'
    ),
    path('<int:course_id>/sections-create/',
         course_content_views.SectionCreateView.as_view(),
         name='section-create'
    ),
    path('<int:course_id>/section/<int:section_id>/',
         course_content_views.SectionDetailView.as_view(),
         name='section-detail'
    ),
    path('<int:section_id>/create-lecture',
         course_content_views.LectureCreateView.as_view(),
         name='lecture-create'
    ),
    path('section/<int:section_id>/lecture/<int:lecture_id>/',
         course_content_views.LectureDetailView.as_view(),
         name='lecture-detail'
    ),

]
