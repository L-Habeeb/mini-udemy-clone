# """
# Category Views
# """
# from rest_framework import (mixins, viewsets)
#
#
# from category import serializers
# from core.models import Category
#
#
# class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """ViewSet for Listing, Detail List"""
#
#     queryset = Category.objects.prefetch_related('subcategory').all()
#     serializer_class = serializers.CategorySerializer
