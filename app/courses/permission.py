"""
Custom Permission for Course API
"""
from rest_framework import permissions

class IsInstructorForCreateOrOwnerForEdit(permissions.BasePermission):
    """
    Custom permission: instructors can create courses,
    - owners can update/delete,
    - Everyone can read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            return getattr(request.user, "role", None) == "instructor"
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user in obj.instructor.all()
