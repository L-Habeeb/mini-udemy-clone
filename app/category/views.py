"""
Category Views
"""
from rest_framework import (mixins, viewsets)

from category import serializers
from core.models import Category


# Admin only will create category in the admin
class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for Category and its SubCategory Listing"""

    queryset = Category.objects.prefetch_related('subcategory').all()
    serializer_class = serializers.CategorySerializer

