"""
Views Handling the four URL
mark-lecture-complete/incomplete and CourseProgress
"""
from django.shortcuts import get_object_or_404
from enrollment import serializers
from core.models import Lecture, Section, Course, Enrollment
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from core.models import LectureProgress, CourseProgress
from progresstracker.serializers import LectureProgressSerializer, CourseProgressSerializer
from progresstracker.permissions import IsEnrolledInLectureCourse


class MarkLectureCompleteView(generics.CreateAPIView):
    """
    Mark Lecture provided from URL complete
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsEnrolledInLectureCourse]
    serializer_class = LectureProgressSerializer
    queryset = LectureProgress.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lecture_id'] = self.kwargs['lecture_id']
        return context


class MarkLectureIncompleteView(generics.UpdateAPIView):
    """
    Mark Lecture provided from URL complete
    """
    serializer_class = LectureProgressSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'lecture'
    lookup_url_kwarg = 'lecture_id'

    def get_queryset(self):
        return LectureProgress.objects.filter(student=self.request.user)


class CourseProgressView(generics.RetrieveAPIView):
    """
    Retrieve CourseProgress for a course
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CourseProgressSerializer
    lookup_url_kwarg = 'course_id'
    lookup_field = 'course'

    def get_queryset(self):
        return CourseProgress.objects.filter(student=self.request.user)


class CourseProgressViewAll(generics.ListAPIView):
    """
    Handles the current Student all Courses Progress
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CourseProgressSerializer

    def get_queryset(self):
        return CourseProgress.objects.filter(student=self.request.user).order_by('-last_accessed')
