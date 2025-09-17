"""
Serializer for adding and removing courses in cart
"""
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.models import Cart, Enrollment, Course
from rest_framework.exceptions import ValidationError as DjangoValidationError


class MyCartSerializers(serializers.ModelSerializer):
    """Handles User Cart List"""
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'student', 'course', 'added_at', 'total_items', 'total_price']
        read_only_fields = ['student', 'course', 'added_at']

    def get_total_items(self, obj):
        user = self.context['request'].user
        return Cart.objects.filter(student=user).count()

    def get_total_price(self, obj):
        user = self.context['request'].user
        total = sum(
            c.course.price for c in Cart.objects.filter(student=user).select_related('course')
        )
        return total


class CartSerializers(serializers.ModelSerializer):
    """Serializer for CREATE, GET, and REMOVE"""

    class Meta:
        model = Cart
        fields = ['id', 'student', 'course', 'added_at']
        read_only_fields = ['student', 'course', 'added_at']


    def validate(self, data):
        course_id = self.context['view'].kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        student = self.context['request'].user
        data['course'] = course
        data['student'] = student
        cart = Cart(**data)
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError(
                "You already enrolled in this course, check your enrollment list"
            )
        if Cart.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError(
                {"error": "Course is already in cart."}
            )
        try:
            cart.full_clean()
            return data
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def create(self, validated_data):
        """Create Cart object"""
        return Cart.objects.create(**validated_data)
