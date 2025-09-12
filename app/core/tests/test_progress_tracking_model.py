"""
Test for Progress Tracking Model
CourseProgress and LectureProgress Model Test
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.signal import signals

from core.models import (
    Course, Section, Lecture,
    LectureProgress, CourseProgress,
    SubCategory, Category, Enrollment)

User = get_user_model()


class LectureProgressModelTest(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            email='student@test.com',
            password='Testpass123!'
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='Testpass123!',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='web development'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            category=self.category,
            price=99.99
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)

        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        self.section = Section.objects.create(
            course=self.course, title="Introduction", order=1
        )
        self.lecture = Lecture.objects.create(
            section=self.section,
            title="Welcome",
            order=1,
            duration=300,
            content_type="video",
            video=video_file
        )

    def test_lecture_progress_completion_auto_sets_timestamp_and_watch_time(self):
        """Test LectureProgress.save() automatically sets completion data"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        progress = LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture,
            is_completed=True
        )

        self.assertIsNotNone(progress.completed_at)
        self.assertEqual(progress.watch_time, 300)

    def test_lecture_progress_incompletion_clears_data(self):
        """Test marking as incomplete clears completion data"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        progress = LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture,
            is_completed=True
        )

        progress.is_completed = False
        progress.save()

        self.assertIsNone(progress.completed_at)
        self.assertEqual(progress.watch_time, 0)


class CourseProgressModelTest(TestCase):

    def setUp(self):
        """Setup course with multiple lectures"""
        self.student = User.objects.create_user(
            email='student@test.com',
            password='Testpass123!'
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='Testpass123!',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='web development'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            category=self.category,
            price=99.99
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)

        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        self.section = Section.objects.create(
            course=self.course, title="Introduction", order=1
        )
        self.lecture1 = Lecture.objects.create(
            section=self.section,
            title="Welcome",
            order=1,
            duration=250,
            content_type="video",
            video=video_file
        )
        self.lecture2 = Lecture.objects.create(
            section=self.section,
            title="Welcome Part 2",
            order=2,
            duration=500,
            content_type="video",
            video=video_file
        )
        self.lecture3 = Lecture.objects.create(
            section=self.section,
            title="Welcome Part 3",
            order=3,
            duration=150,
            content_type="video",
            video=video_file
        )


    def test_course_progress_update_calculates_correctly(self):
        """Test CourseProgress.update_progress() calculates percentages correctly"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course,
            total_lectures=0
        )

        LectureProgress.objects.create(student=self.student, lecture=self.lecture1, is_completed=True)
        LectureProgress.objects.create(student=self.student, lecture=self.lecture2, is_completed=True)

        # Update progress manually
        course_progress.update_progress()

        self.assertEqual(course_progress.completed_lectures, 2)
        self.assertEqual(course_progress.total_lectures, 3)
        self.assertAlmostEqual(float(course_progress.progress_percentage), 66.67, places=1)

    def test_course_progress_signals_auto_update(self):
        """Test Django signals automatically update CourseProgress"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture1,
            is_completed=True
        )

        # Signal should have auto-created CourseProgress
        course_progress = CourseProgress.objects.get(student=self.student, course=self.course)

        # Should show 33.33% (1 out of 3)
        self.assertEqual(course_progress.completed_lectures, 1)
        self.assertEqual(course_progress.total_lectures, 3)
        self.assertAlmostEqual(float(course_progress.progress_percentage), 33.33, places=1)

    def test_course_progress_is_completed_property(self):
        """Test is_completed property returns True at 100%"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course,
            completed_lectures=3,
            total_lectures=3,
            progress_percentage=100
        )

        self.assertTrue(course_progress.is_completed)
