"""
Course API Views
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework import (mixins, viewsets)

from courses import serializers, permission
from core.models import Course, Category
from category import serializers as category_serializer


class CourseViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet for Course Listing, Detail List, Creation, and Update"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permission.IsInstructorForCreateOrOwnerForEdit]

    queryset = Course.objects.prefetch_related('instructor').order_by('-id')
    serializer_class = serializers.CourseSerializer


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for Category and its SubCategory Listing"""

    queryset = Category.objects.prefetch_related('subcategory').all()
    serializer_class = category_serializer.CategorySerializer
