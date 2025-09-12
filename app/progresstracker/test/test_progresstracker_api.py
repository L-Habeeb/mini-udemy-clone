"""
Test for Progress Tracker - Lecture and Progress Tracker API
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import (User, Course, Category, SubCategory,
                         Section, Lecture, Enrollment, LectureProgress,
                         CourseProgress)


class ProgressAPITest(APITestCase):

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

        self.video_file = SimpleUploadedFile(
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
            video=self.video_file
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_mark_lecture_complete_creates_progress_record(self):
        """Test POST /lectures/{id}/mark-complete/ creates LectureProgress"""
        self.client.force_authenticate(user=self.student)

        url = reverse('course:mark-lecture-complete', kwargs={'lecture_id': self.lecture.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check LectureProgress was created
        progress = LectureProgress.objects.get(student=self.student, lecture=self.lecture)
        self.assertTrue(progress.is_completed)
        self.assertIsNotNone(progress.completed_at)
        self.assertEqual(progress.watch_time, 300)

    def test_mark_lecture_incomplete_updates_existing_progress(self):
        """Test POST /lectures/{id}/mark-incomplete/ updates existing progress"""
        self.client.force_authenticate(user=self.student)

        # First mark complete
        LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture,
            is_completed=True
        )

        # Then mark incomplete
        url = reverse('course:mark-lecture-incomplete', kwargs={'lecture_id': self.lecture.id})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check progress was updated
        progress = LectureProgress.objects.get(student=self.student, lecture=self.lecture)
        self.assertFalse(progress.is_completed)
        self.assertIsNone(progress.completed_at)
        self.assertEqual(progress.watch_time, 0)

    def test_mark_complete_requires_enrollment(self):
        """Test marking complete fails if student not enrolled"""
        # Create non-enrolled student
        other_student = User.objects.create_user(
            email='other@test.com',
            password='Testpass123!'
        )
        self.client.force_authenticate(user=other_student)

        url = reverse('course:mark-lecture-complete', kwargs={'lecture_id': self.lecture.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_progress_shows_completion_percentage(self):
        """Test GET /courses/{id}/progress/ returns progress stats"""
        self.client.force_authenticate(user=self.student)

        # Create second lecture
        lecture2 = Lecture.objects.create(
            section=self.section,
            title="Lesson 2",
            order=2,
            duration=400,
            content_type="video",
            video=self.video_file
        )

        # Complete first lecture (signals will auto-create CourseProgress)
        LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture,
            is_completed=True
        )

        url = reverse('course:course-progress', kwargs={'course_id': self.course.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_lectures'], 1)
        self.assertEqual(response.data['total_lectures'], 2)
        self.assertEqual(float(response.data['progress_percentage']), 50.0)

    def test_my_progress_dashboard_lists_all_courses(self):
        """Test GET /progress/ returns progress for all enrolled courses"""
        self.client.force_authenticate(user=self.student)

        # Create second course and enroll
        course2 = Course.objects.create(
            title='Django Basics',
            description='Learn Django',
            category=self.category,
            price=149.99
        )
        course2.instructor.add(self.instructor)
        section2 = Section.objects.create(
            course=course2, title="Introduction", order=1
        )
        lecture2 = Lecture.objects.create(
            section=section2,
            title="Welcome 2",
            order=2,
            duration=300,
            content_type="video",
            video=self.video_file
        )

        Enrollment.objects.create(student=self.student, course=course2)

        LectureProgress.objects.create(
            student=self.student,
            lecture=self.lecture,
            is_completed=True
        )
        LectureProgress.objects.create(
            student=self.student,
            lecture=lecture2,
            is_completed=True
        )

        url = reverse('course:my-progress')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_unauthenticated_user_cannot_access_progress(self):
        """Test authentication required for all progress endpoints"""
        # Test mark complete
        url = reverse('course:mark-lecture-complete', kwargs={'lecture_id': self.lecture.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test course progress
        url = reverse('course:course-progress', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test dashboard
        url = reverse('course:my-progress')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
