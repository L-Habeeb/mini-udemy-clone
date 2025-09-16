"""
Course API Views
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.authentication import TokenAuthentication
from rest_framework import (mixins, viewsets)

from courses import serializers, permission
from core.models import Course, Category
from category import serializers as category_serializer

from django.db.models import Q, Avg, Count
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Case, When, Value, FloatField


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


@extend_schema(
    parameters=[
        OpenApiParameter(name='q', description='Search in title & description', required=False, type=str),
        OpenApiParameter(name='category', description='Filter by category name', required=False, type=str),
        OpenApiParameter(name='subcategory', description='Filter by subcategory name', required=False, type=str),
        # ...

    ]
)

class CourseSearchView(generics.ListAPIView):
    """
    API endpoint for searching and filtering courses

    Query Parameters:
    - q: Text search in title and description
    - category: Filter by category name
    - subcategory: Filter by subcategory name
    - level: Filter by course level
    - min_rating: Filter by minimum average rating
    - sort: Sort results (rating, newest, price)
    """
    serializer_class = serializers.CourseSerializer
    # pagination_class = None

    def get_queryset(self):
        """Build filtered queryset based on query parameters"""
        queryset = Course.objects.select_related('category').prefetch_related(
            'subcategory', 'instructor', 'reviews'
        )

        # Get query parameters
        query = self.request.query_params.get('q', '').strip()
        category = self.request.query_params.get('category', '').strip()
        subcategory = self.request.query_params.get('subcategory', '').strip()
        level = self.request.query_params.get('level', '').strip()
        min_rating = self.request.query_params.get('min_rating')
        sort_by = self.request.query_params.get('sort', 'newest')

        if query:
            queryset = self._apply_text_search(queryset, query)

        if category:
            queryset = self._apply_category_filter(queryset, category)

        if subcategory:
            queryset = self._apply_subcategory_filter(queryset, subcategory)

        if level:
            queryset = self._apply_level_filter(queryset, level)

        if min_rating:
            queryset = self._apply_rating_filter(queryset, min_rating)

        queryset = self._apply_sorting(queryset, sort_by)

        return queryset

    def _apply_text_search(self, queryset, query):
        """Apply text search in title and description"""
        return queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    def _apply_category_filter(self, queryset, category_name):
        """Filter by category name"""
        return queryset.filter(category__name__icontains=category_name)

    def _apply_subcategory_filter(self, queryset, subcategory_name):
        """Filter by subcategory name"""
        return queryset.filter(subcategory__name__icontains=subcategory_name)

    def _apply_level_filter(self, queryset, level):
        """Filter by course level"""
        return queryset.filter(level=level)

    def _apply_rating_filter(self, queryset, min_rating):
        """Filter by minimum average rating"""
        try:
            min_rating_value = float(min_rating)
            return queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=min_rating_value)
        except (ValueError, TypeError):
            return queryset

    def _apply_sorting(self, queryset, sort_by):
        """Apply sorting to queryset"""
        if sort_by == 'rating':
            return queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-created_at')

        elif sort_by == 'price':
            return queryset.order_by('price', '-created_at')

        elif sort_by == 'newest':
            return queryset.order_by('-created_at')

        else:
            return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """Override list to add search metadata"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
