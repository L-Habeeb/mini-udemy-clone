"""
Custom Permission for Admin
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Only staff can modify Category data.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff
