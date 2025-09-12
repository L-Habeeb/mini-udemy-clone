"""
Custome Permission to check if enrolled
"""
from rest_framework.permissions import BasePermission
from core.models import Enrollment, Lecture

class IsEnrolledInLectureCourse(BasePermission):
    """
    Only allow access if the requesting user is enrolled
    in the course that owns this lecture.
    """

    message = 'You must be enrolled in this course to mark progress.'

    def has_permission(self, request, view):
        lecture_id = view.kwargs.get('lecture_id')
        if not lecture_id:
            return False
        try:
            lecture = Lecture.objects.get(pk=lecture_id)
        except Lecture.DoesNotExist:
            return False

        return Enrollment.objects.filter(
            student=request.user,
            course=lecture.section.course
        ).exists()
