"""
Serializer for CourseReview
"""
from rest_framework import serializers
from core.models import CourseReview, User, Course, Enrollment
from django.shortcuts import get_object_or_404


class CourseReviewSerializer(serializers.ModelSerializer):
    """
    CourseReview Serializer handles GET | POST | UPDATE
    """

    class Meta:
        model = CourseReview
        fields = ['id', 'student', 'course', 'rating', 'review_text']
        read_only_fields = ['student', 'course']

    def validate(self, data):
        """Simplified validation - let model handle business logic"""
        request = self.context['request']
        course_id = self.context.get('course_id')

        if not course_id:
            raise serializers.ValidationError("Course ID is required")

        if not self.instance:
            course = get_object_or_404(Course, id=course_id)

            if CourseReview.objects.filter(
                    student=request.user,
                    course=course
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this course"
                )

            data['student'] = request.user
            data['course'] = course

        return data

    def create(self, validated_data):
        return CourseReview.objects.create(**validated_data)
