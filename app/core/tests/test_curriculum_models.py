from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Category, SubCategory, Course, Section, Lecture


class BaseModelTestCase(TestCase):
    """Base test case providing common setup for Section and Lecture test."""

    def setUp(self):
        """Create test data with lectures for aggregation testing"""
        self.user = get_user_model().objects.create_user(
            email='instructor@example.com',
            name='Test Instructor',
            password='Testpass@123',
            role='instructor'
        )

        self.category = Category.objects.create(name='Technology')
        self.subcategory = SubCategory.objects.create(
            name='Web Development',
            category=self.category
        )

        self.course = Course.objects.create(
            title='Complete Web Development',
            description='Learn web development from scratch',
            category=self.category,
            language='English',
            level='Beginner',
            price=Decimal('99.99')
        )
        self.course.instructor.add(self.user)
        self.course.subcategory.add(self.subcategory)


class SectionModelTests(BaseModelTestCase):
    """Tests for the Section model."""

    def test_section_creation_with_valid_data(self):
        section = Section.objects.create(
            title="Introduction",
            course=self.course,
            order=1
        )
        self.assertEqual(section.title, "Introduction")
        self.assertEqual(section.course, self.course)
        self.assertEqual(section.order, 1)

    def test_section_title_required(self):
        section = Section(course=self.course, order=1)
        with self.assertRaises(ValidationError):
            section.full_clean()

    def test_section_course_required(self):
        with self.assertRaises(Exception):
            Section.objects.create(
                title="No Course",
                order=1
            )

    def test_multiple_sections_same_course(self):
        Section.objects.create(
            title="Intro",
            course=self.course,
            order=1
        )
        Section.objects.create(
            title="Advanced",
            course=self.course,
            order=2
        )
        self.assertEqual(self.course.sections.count(), 2)

    def test_section_ordering(self):
        s1 = Section.objects.create(
            title="B",
            course=self.course,
            order=2
        )
        s2 = Section.objects.create(
            title="A",
            course=self.course,
            order=1
        )
        sections = Section.objects.filter(course=self.course)
        self.assertEqual(list(sections), [s2, s1])

    def test_section_deletion_leaves_course_intact(self):
        Section.objects.create(
            title="Temp",
            course=self.course,
            order=1
        )
        self.course.sections.all().delete()
        self.course.refresh_from_db()
        self.assertTrue(Course.objects.filter(id=self.course.id).exists())


class LectureModelTests(BaseModelTestCase):
    """Basic Lecture creation and validation test."""

    def setUp(self):
        super().setUp()
        self.section = Section.objects.create(
            title="Intro",
            course=self.course,
            order=1
        )

    def test_lecture_creation_and_required_fields(self):
        """Test lecture creation with required fields and validation"""
        lecture = Lecture.objects.create(
            title='Introduction Video',
            section=self.section,
            content_type='video',
            duration=308,
            order=1,
            is_preview=True,
            content='path/to/video.mp4'
        )

        self.assertEqual(lecture.title, 'Introduction Video')
        self.assertEqual(lecture.section, self.section)
        self.assertEqual(lecture.content_type, 'video')
        self.assertEqual(lecture.duration, 308)
        self.assertTrue(lecture.is_preview)
        self.assertEqual(lecture.content, 'path/to/video.mp4')

        lecture = Lecture(
                title='Test Lecture',
                section=None,
                content_type='video',
                duration=180,
                order=4
        )
        with self.assertRaises(ValidationError):
                lecture.full_clean()

        with self.assertRaises(ValidationError):
            invalid_lecture = Lecture(
                title='Empty Content',
                section=self.section,
                content_type='article',
                duration=0,
                order=3,
                content=''
            )
            invalid_lecture.full_clean()

    def test_invalid_content_type_rejected(self):
        with self.assertRaises(Exception):
            Lecture.objects.create(title="Invalid", section=self.section, content_type="podcast")

    def test_lecture_ordering_within_section(self):
        """Test lecture ordering logic within section"""
        lecture3 = Lecture.objects.create(
            title='HTML Best Practices 1',
            section=self.section,
            content_type='article',
            duration=600,
            order=3,
            is_preview=False
        )
        lecture1 = Lecture.objects.create(
            title='HTML Best Practices 3',
            section=self.section,
            content_type='article',
            duration=600,
            order=1,
            is_preview=False
        )
        lecture2 = Lecture.objects.create(
            title='HTML Best Practices',
            section=self.section,
            content_type='article',
            duration=600,
            order=2,
            is_preview=False
        )

        ordered_lectures = self.section.lectures.all().order_by('order')
        self.assertEqual(list(ordered_lectures), [lecture1, lecture2, lecture3])

    def test_lecture_content_required(self):
        with self.assertRaises(Exception):
            Lecture.objects.create(section=self.section)


class LectureValidationTests(BaseModelTestCase):
    """Business rules validation for different lecture types."""

    def setUp(self):
        super().setUp()
        self.section = Section.objects.create(
            title="Validation Section",
            course=self.course,
            order=1
        )

    def test_invalid_content_type_rejected(self):
        """Test that invalid content types are rejected"""
        with self.assertRaises(ValidationError):
            lecture = Lecture(
                title='Invalid Lecture',
                section=self.section,
                content_type='invalid_type',
                duration=180,
                order=1,
                content='some content'
            )
            lecture.full_clean()

    def test_lecture_ordering_within_different_sections(self):
        s2 = Section.objects.create(
            title="Second Section",
            course=self.course,
            order=2
        )
        l1 = Lecture.objects.create(
            title='HTML Best Practices',
            section=s2,
            content_type='article',
            duration=600,
            order=1,
            is_preview=False
        )
        l2 = Lecture.objects.create(
            title='HTML Best Practices 2',
            section=self.section,
            content_type='article',
            duration=60,
            order=3,
            is_preview=False
        )
        self.assertEqual(l1.order, 1)
        self.assertEqual(l2.order, 3)


class SectionAggregationTests(BaseModelTestCase):
    """Tests for aggregation logic on Section (lecture count, duration, preview)."""

    def setUp(self):
        super().setUp()
        self.section = Section.objects.create(
            title="Aggregation",
            course=self.course,
            order=1
        )

    def test_section_lecture_count_duration_with_lectures(self):
        Lecture.objects.create(
            title='HTML Best Practices 5',
            section=self.section,
            content_type='article',
            duration=600,
            order=1,
            is_preview=False
        )
        Lecture.objects.create(
            title='HTML Best Practices 10',
            section=self.section,
            content_type='article',
            duration=600,
            order=4,
            is_preview=False
        )
        self.assertEqual(self.section.lectures.count(), 2)
        self.assertEqual(sum(l.duration for l in self.section.lectures.all()), 1200)

    def test_lecture_deletion_updates_section_aggregates(self):
        lecture = Lecture.objects.create(title="To Delete", section=self.section, content_type="video", duration=20, order=1)
        lecture.delete()
        self.assertEqual(self.section.lectures.count(), 0)

    def test_preview_lecture_filtering(self):
        """Test preview system for access control"""
        preview_lecture = Lecture.objects.create(
            title='Preview Lecture',
            section=self.section,
            content_type='video',
            duration=180,
            order=1,
            is_preview=True
        )
        regular_lecture = Lecture.objects.create(
            title='Premium Content',
            section=self.section,
            content_type='video',
            duration=300,
            order=2,
            is_preview=False
        )

        preview_lectures = self.section.lectures.filter(is_preview=True)
        self.assertEqual(preview_lectures.count(), 1)
        self.assertIn(preview_lecture, preview_lectures)
        self.assertNotIn(regular_lecture, preview_lectures)

class CurriculumPerformanceTests(BaseModelTestCase):
    """Test suite for performance and query optimization"""

    def setUp(self):
        super().setUp()
        self.section = Section.objects.create(
            title='HTML Fundamentals',
            course=self.course,
            order=1
        )

    def test_efficient_section_lecture_queries(self):
        """Test N+1 query prevention for section-lecture relationships"""
        for i in range(5):
            Lecture.objects.create(
                title=f'Lecture {i + 1}',
                section=self.section,
                content_type='video',
                duration=300,
                order=i + 1,
                content=f'video_{i + 1}.mp4'
            )

        with self.assertNumQueries(2):
            section = Section.objects.get(id=self.section.id)
            lectures = list(section.lectures.all())
            for lecture in lectures:
                _ = lecture.title
                _ = lecture.content_type
                _ = lecture.duration

