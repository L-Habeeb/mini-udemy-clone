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
from enrollment import views as enrollment_views
from progresstracker import views as progresstracker_views
from coursereview import views as coursereview_views


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

    path('course/<int:course_id>/enroll',
             enrollment_views.EnrollmentCreateView.as_view(),
             name='enroll'
    ),

    path('my-enrollments',
             enrollment_views.EnrollmentViews.as_view(),
             name='my-enrollments'
    ),

    path('course/<int:course_id>/course-enrollment-stats',
             enrollment_views.CourseEnrollmentViews.as_view(),
             name='course-enrollment-stats'
    ),

    # progress_tracker URLS
    path('lectures/<int:lecture_id>/mark-lecture-complete',
             progresstracker_views.MarkLectureCompleteView.as_view(),
             name='mark-lecture-complete'
    ),
    path('lectures/<int:lecture_id>/mark-lecture-incomplete',
             progresstracker_views.MarkLectureIncompleteView.as_view(),
             name='mark-lecture-incomplete'
    ),
    path('courses/<int:course_id>/course-progress',
             progresstracker_views.CourseProgressView.as_view(),
             name='course-progress'
    ),
    path('my-progress',
             progresstracker_views.CourseProgressViewAll.as_view(),
             name='my-progress'
    ),

    # CourseReview URLS
    path('<int:course_id>/reviews',
             coursereview_views.CourseReviewView.as_view(),
             name='course-review-create'
    ),
    path('<int:course_id>/reviews',
             coursereview_views.CourseReviewView.as_view(),
             name='course-review-list'
    ),
    path('<int:course_id>/reviews/<int:course_review_id>',
             coursereview_views.CourseReviewUpdateView.as_view(),
             name='course-review-update'
    ),

    # Searching
    path('courses/search/', views.CourseSearchView.as_view(), name='course-search'),
]
