"""
Serializers for Lecture and Course Progress
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.models import LectureProgress, CourseProgress, Lecture, Enrollment


class LectureProgressSerializer(serializers.ModelSerializer):
    """
    Serializer handling POST GET
    """

    class Meta:
        model = LectureProgress
        fields = [
            'id', 'student', 'lecture', 'is_completed', 'completed_at',
            'watch_time', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'student', 'lecture', 'is_completed', 'completed_at',
            'watch_time', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """
        Creating a new LectureProgress when POST set Lecture completed
        """
        lecture_id = self.context['lecture_id']
        if not lecture_id:
            raise serializers.ValidationError("Lecture ID not provided from url")
        lecture = get_object_or_404(Lecture, id=lecture_id)
        lecture_progress, created = LectureProgress.objects.get_or_create(
            student=self.context['request'].user,
            lecture=lecture
        )
        lecture_progress.is_completed = True
        lecture_progress.save()
        return lecture_progress

    def update(self, instance, validated_data):
        """
        Mark incomplete.
        """
        instance.is_completed = False
        instance.save()
        return instance


class CourseProgressSerializer(serializers.ModelSerializer):
    """
    Serializer Handling CourseProgress Object
    """

    class Meta:
        model = CourseProgress
        fields = [
            'id', 'student', 'course', 'completed_lectures', 'total_lectures',
            'progress_percentage', 'last_accessed', 'created_at'
        ]
        read_only_fields = [
            'student', 'course', 'completed_lectures', 'total_lectures',
            'progress_percentage', 'last_accessed', 'created_at'
        ]
