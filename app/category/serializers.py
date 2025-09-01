"""
Serializer for Category
"""
from core.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Categories and its Subcategories"""
    subcategory = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
        allow_null=True,
     )

    class Meta:
        model = Category
        fields = ['name', 'subcategory']
