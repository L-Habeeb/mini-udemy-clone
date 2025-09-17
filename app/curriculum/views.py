"""
Course API Views
"""
from django.shortcuts import get_object_or_404

from curriculum import serializers
from core.models import Lecture, Section, Course
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from curriculum.permissions import (IsLectureInstructor,
                         IsSectionLectureInstructor,
                         IsSectionInstructor,
                         IsCourseInstructor)

class LectureCreateView(generics.CreateAPIView):
    """
    POST /section/{id}/
    Create new section
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSectionLectureInstructor]
    serializer_class = serializers.LectureCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_id'] = self.kwargs.get('section_id')

        return context


class LectureDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /section/{section_id}/lecture/{lecture_id}/
    PUT/PATCH/DELETE section
    """
    serializer_class = serializers.LectureSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsLectureInstructor]
    lookup_url_kwarg = "lecture_id"

    def get_queryset(self):
        lecture_id = self.kwargs.get('lecture_id')
        return Lecture.objects.filter(id=lecture_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_id'] = self.kwargs.get('section_id')
        context['lecture_id'] = self.kwargs.get('lecture_id')

        return context


class SectionCreateView(generics.CreateAPIView):
    """
    POST /courses/{id}/sections/
    Create new section
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = serializers.SectionCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_id'] = self.kwargs.get('course_id')

        return context


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /courses/{course_id}/sections/{section_id}/
    PUT/PATCH/DELETE section
    """
    serializer_class = serializers.SectionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSectionInstructor]
    lookup_url_kwarg = "section_id"

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Section.objects.filter(course=course_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_id'] = self.kwargs.get('course_id')
        context['section_id'] = self.kwargs.get('section_id')

        return context


class CurriculumViews(generics.RetrieveAPIView):
    """
    GET /courses/{id}/curriculum/
    Retrieve complete curriculum structure for a course
    Lecture shows ID only
    """
    # permission_classes = [IsCourseInstructor]
    # authentication_classes = [TokenAuthentication]
    serializer_class = serializers.CurriculumSerializer
    lookup_url_kwarg = 'course_id'
    queryset = Course.objects.all()

    def get_object(self):
        """Get course with prefetched curriculum data"""
        course_id = self.kwargs['course_id']
        return get_object_or_404(
            Course.objects.prefetch_related(
                'sections__lectures'
            ),
            id=course_id
        )
