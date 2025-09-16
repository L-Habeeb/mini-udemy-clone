"""
Views for handling POST, GET & UPDATE CourseReview
"""
from coursereview.serializers import CourseReviewSerializer
from core.models import Lecture, Section, Course, Enrollment, CourseReview
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from coursereview.permissions import CanUpdateOwnCourseReview
from rest_framework.response import Response


class CourseReviewView(generics.ListCreateAPIView):
    """CourseReview: Handle POST AND GET"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CourseReviewSerializer

    def get_queryset(self):
        """Optimized queryset"""
        course_id = self.kwargs.get('course_id')
        return CourseReview.objects.filter(course_id=course_id).select_related(
            'student'
        ).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_id'] = self.kwargs.get('course_id')
        return context

    def create(self, request, *args, **kwargs):
        """
        Create review with enrollment validation
        """
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        if not Enrollment.objects.filter(
                student=request.user,
                course=course
        ).exists():
            return Response(
                {'detail': 'You must be enrolled in this course to create a review.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)


class CourseReviewUpdateView(generics.UpdateAPIView):
    """
    CourseReview: Handles Update(PUT/PATCH)
    by providing review id from URL
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [CanUpdateOwnCourseReview]
    serializer_class = CourseReviewSerializer
    lookup_url_kwarg = 'course_review_id'

    def get_queryset(self):
        """Optimized queryset for updates"""
        course_id = self.kwargs.get('course_id')
        return CourseReview.objects.filter(
            course_id=course_id
        ).select_related('student', 'course')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_id'] = self.kwargs.get('course_id')
        return context
