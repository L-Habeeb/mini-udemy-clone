"""
Curriculum API Permissions
"""
from rest_framework import permissions

from core.models import Course, Section, Lecture


class IsCourseInstructor(permissions.BasePermission):
    """
    Custom permission to only allow course instructors to modify curriculum.
    For course-level operations: /courses/{id}/curriculum/ or /courses/{id}/sections/
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and is instructor of the course"""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        course_id = view.kwargs.get('course_id') or view.kwargs.get('pk')
        if not course_id:
            return False

        try:
            course = Course.objects.get(id=course_id)
            return course.instructor.filter(id=request.user.id).exists()
        except Course.DoesNotExist:
            return False


class IsSectionInstructor(permissions.BasePermission):
    """
    Custom permission for section-level operations: /sections/{id}/
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and is instructor of the section's course"""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        section_id = view.kwargs.get('section_id') or view.kwargs.get('pk')
        if not section_id:
            return False

        try:
            section = Section.objects.select_related('course').get(id=section_id)
            return section.course.instructor.filter(id=request.user.id).exists()
        except Section.DoesNotExist:
            return False


class IsLectureInstructor(permissions.BasePermission):
    """
    Custom permission for lecture-level operations: /lectures/{id}/
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and is instructor of the lecture's course"""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        lecture_id = view.kwargs.get('lecture_id') or view.kwargs.get('pk')
        if not lecture_id:
            return False

        try:
            lecture = Lecture.objects.select_related('section__course').get(id=lecture_id)
            return lecture.section.course.instructor.filter(id=request.user.id).exists()
        except Lecture.DoesNotExist:
            return False


class IsSectionLectureInstructor(permissions.BasePermission):
    """
    Custom permission for section-lecture operations: /sections/{id}/lectures/
    """

    def has_permission(self, request, view):
        """Check if user is instructor of the section's course"""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        section_id = view.kwargs.get('section_id')
        if not section_id:
            return False

        try:
            section = Section.objects.select_related('course').get(id=section_id)
            return section.course.instructor.filter(id=request.user.id).exists()
        except Section.DoesNotExist:
            return False
