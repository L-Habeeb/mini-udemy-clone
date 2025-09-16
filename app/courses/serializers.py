"""
Serializer for Course API
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import (Course,
                         Category,
                         SubCategory)

def slug_field_helper(slug_field, queryset, **kwargs):
    return serializers.SlugRelatedField(
        **kwargs,
        slug_field=slug_field,
        queryset=queryset
    )

class CourseSerializer(serializers.ModelSerializer):
    """Serializing The Course Model"""
    instructor = slug_field_helper('email', get_user_model().objects.all(), many=True, required=True,)
    category = slug_field_helper('name', Category.objects.all())
    subcategory = slug_field_helper('name', SubCategory.objects.all(), many=True, required=True,)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            'id', 'category', 'subcategory', 'title',
            'description', 'objectives', 'instructor',
            'language', 'level', 'price', 'average_rating'
        ]


    def validate_instructor(self, value):
        """Ensure all provided instructors have role='instructor'."""
        for user in value:
            if user.role != "instructor":
                raise serializers.ValidationError(
                    f"{user.email} is not an instructor."
                )
        return value

    def create(self, validated_data):
        auth_user = self.context['request'].user
        other_instructor = validated_data.pop('instructor', [])
        category_input = validated_data.pop('category', '')
        subcategory_input = validated_data.pop('subcategory', [])
        course_instance = Course.objects.create(category=category_input, **validated_data)

        course_instance.instructor.add(auth_user)
        course_instance.subcategory.set(subcategory_input)

        if other_instructor:
            course_instance.instructor.add(*other_instructor)
        return course_instance

    def update(self, instance, validated_data):
        """Custom update method to preserve instructors when not explicitly provided"""
        instructors = validated_data.pop('instructor', None)
        subcategory_input = validated_data.pop('subcategory', None)
        category_input = validated_data.pop('category', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instructors is not None:
            instance.instructor.set(instructors)
        if category_input is not None:
            instance.category = category_input
        if subcategory_input is not None:
            instance.subcategory.set(subcategory_input)
        instance.save()
        return instance
