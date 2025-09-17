"""
Curriculum API Serializers
"""
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import Course, Section, Lecture, User


class LectureSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Lectures with section ID as request
    """

    class Meta:
        model = Lecture
        fields = [
            'section', 'title','order',
            'duration', 'content_type',
            'is_preview','video', 'article', 'file',
        ]
        extra_kwargs = {
            'section': {'read_only': True},
            'content_type': {'write_only': True},
            'is_preview': {'write_only': True},
        }

    def validate(self, data):
        """Validate Data"""
        section_id = self.context.get("section_id")
        section = get_object_or_404(Section, id=section_id)
        lecture_instance = Lecture(section=section, **data)
        if not self.instance:
            try:
                lecture_instance.clean()
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)

        request = self.context.get('request')
        if section and request and request.user.is_authenticated:
            if not section.course.instructor.filter(id=request.user.id).exists():
                raise serializers.ValidationError(
                    "You don't have permission to add Lecture in this section"
                )

        return data

    def validate_order(self, value):
        """Order No Must be Unique within Section"""
        section_id = self.context['view'].kwargs.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        if section and self.instance:
            if Lecture.objects.filter(section=section, order=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Order number already exist"
                )

        elif Lecture.objects.filter(section=section_id, order=value).exists():
            raise serializers.ValidationError(
                "Order number already exist"
            )

        return value

    def validate_title(self, value):
        """Title Must be Unique within Section"""
        section_id = self.context['view'].kwargs.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        if section and self.instance:
            if (Lecture.objects.filter(section=section, title=value).
                    exclude(pk=self.instance.pk).exists()):
                raise serializers.ValidationError(
                    "Title already exist"
                )

        elif Lecture.objects.filter(section=section, title=value).exists():
            raise serializers.ValidationError(
                "Title already exist"
            )

        return value

    def create(self, validated_data):
        """Create New Lecture with section ID"""
        try:
            instance = Lecture.objects.create(**validated_data)
            return instance
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        """Update existing lecture"""
        new_content_type = validated_data.get('content_type', instance.content_type)

        if new_content_type == 'video':
            instance.article = None
            instance.file = None
        elif new_content_type == 'article':
            instance.video = None
            instance.file = None
        elif new_content_type == 'file':
            instance.video = None
            instance.article = None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return instance

class LectureCreateSerializer(LectureSerializer):
    """
    Creating Lectures within Section, context gotten from context
    endpoint looks like - .../section/<pk:id>/
    """

    def create(self, validated_data):
        section_id = self.context.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        if not section:
            raise serializers.ValidationError(
                "Section ID required from url"
            )
        validated_data['section'] = section
        return super().create(validated_data)


class SectionSerializer(serializers.ModelSerializer):
    """
    Section serializer with nested lectures support.
    Handles both read and write operations.
    """
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'title', 'order', 'course', 'lectures',
            'lecture_count', 'total_duration', 'course_title'
        ]
        extra_kwargs = {
            'course': {'read_only': True},
            'lectures': {'read_only': True}
        }

    def validate(self, data):
        """validate Section Post requests"""
        course_id = self.context.get("course_id")
        if not course_id:
            raise serializers.ValidationError("Course ID is required")

        course = get_object_or_404(Course, id=course_id)
        request = self.context.get('request')

        if course and request and request.user.is_authenticated:
            if not course.instructor.filter(id=request.user.id).exists():
                raise serializers.ValidationError(
                    "You don't have permission to add Section in this Course"
                )

        order = data.get('order')
        if order is not None:
            order_filter = course.sections.filter(order=order)
            if self.instance:
                order_filter = order_filter.exclude(pk=self.instance.pk)
            if order_filter.exists():
                raise serializers.ValidationError({
                    'order': "Order number already exists in this course"
                })

        title = data.get('title')
        if title:
            title_filter = course.sections.filter(title=title)
            if self.instance:
                title_filter = title_filter.exclude(pk=self.instance.pk)
            if title_filter.exists():
                raise serializers.ValidationError({
                    'title': "Title already exists in this course"
                })

        section_data = data.copy()
        section_data['course'] = course
        section_instance = Section(**section_data)
        try:
            section_instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        data['course'] = course
        return data

    def create(self, validated_data):
        """Create Section"""
        section_instance = Section(**validated_data)
        try:
            section_instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        section_instance.save()

        return section_instance

    def update(self, instance, validated_data):
        """Update Section"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance


class SectionCreateSerializer(SectionSerializer):
    """Section Create with course provided via context"""

    def create(self, validated_data):
        """Create section with course from context"""
        course_id = self.context["view"].kwargs.get("course_id")
        if not course_id:
            raise serializers.ValidationError(
                "Course ID must be provided from url"
            )
        course = get_object_or_404(Course, id=course_id)
        validated_data['course'] = course
        return super().create(validated_data)


class CurriculumSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying complete curriculum structure.
    """
    sections = SectionSerializer(many=True, read_only=True)
    total_sections = serializers.IntegerField(read_only=True)
    total_lectures = serializers.IntegerField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'total_sections',
            'total_lectures', 'total_duration', 'sections'
        ]

    def to_representation(self, instance):
        """Add computed curriculum statistics."""
        data = super().to_representation(instance)
        sections = instance.sections.all()
        data['total_sections'] = sections.count()

        total_lectures = 0
        total_duration = 0

        for section in sections:
            total_lectures += section.lecture_count
            total_duration += section.total_duration

        data['total_lectures'] = total_lectures
        data['total_duration'] = total_duration

        return data
