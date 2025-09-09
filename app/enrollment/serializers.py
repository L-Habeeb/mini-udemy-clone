"""
Enrollment API Serializers
"""
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from core.models import Course, User, Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    """EnrollmentSerializer"""
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'enrolled_at']
        read_only_fields = ['course', 'enrolled_at', 'student', 'course_title']

    def validate(self, data):
        user_obj = self.context.get('request').user
        if not self.context['course_id']:
            raise serializers.ValidationError("Course ID not provided from url")
        course_obj = get_object_or_404(Course, id=self.context['course_id'])
        data['course'] = course_obj
        data['student'] = user_obj
        enrollment = Enrollment(**data)
        try:
            enrollment.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def create(self, validated_data):
        try:
            enrollment = Enrollment.objects.create(**validated_data)
            return enrollment
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class CourseWithStudentEnrollments(serializers.ModelSerializer):
    student_email = serializers.CharField(source='student.email', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student_email', 'enrolled_at']


class CourseEnrollments(serializers.ModelSerializer):
    """Handles all Enrolled Student per course"""
    total_enrollments = serializers.IntegerField(read_only=True)
    course_title = serializers.CharField(source='title', read_only=True)
    students = CourseWithStudentEnrollments(source='enrollments', many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'course_title', 'total_enrollments', 'students']
