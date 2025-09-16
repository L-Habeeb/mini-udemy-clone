from rest_framework.permissions import BasePermission

class CanUpdateOwnCourseReview(BasePermission):
    """
    Allow only the owner to update/delete their course review.
    This permission is specifically for write operations.
    """
    message = "You can only update or delete your own course reviews."

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return obj.student == request.user
        return False
