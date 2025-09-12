"""
Enrollment API View
"""
from django.shortcuts import get_object_or_404

from enrollment import serializers
from core.models import Lecture, Section, Course, Enrollment
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class EnrollmentViews(generics.ListAPIView):
    """Get Enrollment list for student"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        return Enrollment.objects.filter(student=user).select_related("course")


class CourseEnrollmentViews(generics.RetrieveAPIView):
    """Get Enrollment stat for course"""
    serializer_class = serializers.CourseEnrollments
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.all()


class EnrollmentCreateView(generics.CreateAPIView):
    """Enroll Student to Courses """
    serializer_class = serializers.EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs['course_id']
        context['course_id'] = course_id
        return context
