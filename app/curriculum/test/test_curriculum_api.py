# tests/test_curriculum_api.py
"""
Tests for Curriculum API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Course, Category, SubCategory, Section, Lecture

User = get_user_model()


class CurriculumAPITestCase(APITestCase):
    def setUp(self):
        # Users
        self.instructor = User.objects.create_user(
            email="instructor@example.com",
            password="pass123",
            role="instructor"
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="pass123",
            role="student"
        )

        # Category + SubCategory
        self.category = Category.objects.create(name="Development")
        self.subcategory = SubCategory.objects.create(
            category=self.category, name="Web Development"
        )

        # Course owned by instructor
        self.course = Course.objects.create(
            title="Django Course",
            description="Learn Django",
            price=20,
            category=self.category,
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)

        # Section
        self.section = Section.objects.create(
            course=self.course, title="Introduction", order=1
        )

        # Create a mock video file for the lecture
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )

        # Lecture
        self.lecture = Lecture.objects.create(
            section=self.section,
            title="Welcome",
            order=1,
            duration=50,
            content_type="video",
            video=video_file
        )

        # URLs
        self.curriculum_url = reverse("course:curriculum-detail", args=[self.course.id])
        self.section_create_url = reverse(
            "course:section-create", args=[self.course.id]
        )
        self.section_detail_url = reverse(
            "course:section-detail", args=[self.course.id, self.section.id]
        )
        self.lecture_create_url = reverse(
            "course:lecture-create", args=[self.section.id]
        )
        self.lecture_detail_url = reverse(
            "course:lecture-detail", args=[self.section.id, self.lecture.id]
        )

    # -------------------------
    # Curriculum View
    # -------------------------
    def test_anyone_can_retrieve_curriculum(self):
        response = self.client.get(self.curriculum_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # Section Tests
    # -------------------------
    def test_instructor_can_create_section(self):
        self.client.force_authenticate(self.instructor)
        response = self.client.post(
            self.section_create_url, {
                "title": "New Section",
                "order": 2
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_section(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            self.section_create_url, {"title": "Hack Section", "order": 3}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_update_section(self):
        self.client.force_authenticate(self.instructor)
        response = self.client.patch(
            self.section_detail_url, {"title": "Updated Intro"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        self.assertEqual(self.section.title, "Updated Intro")

    def test_instructor_can_delete_section(self):
        self.client.force_authenticate(self.instructor)
        response = self.client.delete(self.section_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # -------------------------
    # Lecture Tests
    # -------------------------
    def test_instructor_can_create_lecture(self):
        self.client.force_authenticate(self.instructor)

        # Create a mock video file
        video_file = SimpleUploadedFile(
            "new_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )

        payload = {
            "title": "New Lecture",
            "order": 2,
            "duration": 15,
            "content_type": "video",
            "video": video_file
        }
        response = self.client.post(self.lecture_create_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_instructor_can_create_article_lecture(self):
        """Test creating an article lecture (no file upload needed)"""
        self.client.force_authenticate(self.instructor)

        payload = {
            "title": "Article Lecture",
            "order": 3,
            "duration": 0,
            "content_type": "article",
            "article": "This is the article content"
        }
        response = self.client.post(self.lecture_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_lecture(self):
        self.client.force_authenticate(self.student)

        # Use article type to avoid file upload issues
        payload = {
            "title": "Hack Lecture",
            "order": 3,
            "duration": 0,
            "content_type": "article",
            "article": "Hack content"
        }
        response = self.client.post(self.lecture_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_update_lecture_title_only(self):
        """Test updating only the title by including required fields"""
        self.client.force_authenticate(self.instructor)

        # For the current validation, we need to include content_type and duration
        response = self.client.patch(
            self.lecture_detail_url,
            {
                "title": "Updated Lecture Title",
                "content_type": "video",  # Required field
                "duration": 10  # Required field
            }
        )
        print(f"{response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lecture.refresh_from_db()
        self.assertEqual(self.lecture.title, "Updated Lecture Title")

    def test_instructor_can_update_lecture_with_full_content(self):
        """Test updating lecture with proper content validation"""
        self.client.force_authenticate(self.instructor)

        # Create a new video file for update
        new_video_file = SimpleUploadedFile(
            "updated_video.mp4",
            b"updated_content",
            content_type="video/mp4"
        )

        # PUT requires ALL fields
        payload = {
            "title": "Updated Video Lecture",
            "order": 1,  # Required field
            "duration": 20,
            "content_type": "video",
            "video": new_video_file
        }

        response = self.client.put(
            self.lecture_detail_url,
            payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lecture.refresh_from_db()
        self.assertEqual(self.lecture.title, "Updated Video Lecture")
        self.assertEqual(self.lecture.duration, 20)

    def test_instructor_can_update_lecture_to_article(self):
        """Test changing content type from video to article"""
        self.client.force_authenticate(self.instructor)

        payload = {
            "title": "Converted to Article",
            "order": 1,
            "duration": 0,
            "content_type": "article",
            "article": "This is the new article content"
        }

        response = self.client.put(
            self.lecture_detail_url,
            payload
        )
        print(f"{response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lecture.refresh_from_db()
        self.assertEqual(self.lecture.title, "Converted to Article")
        self.assertEqual(self.lecture.content_type, "article")
        self.assertEqual(self.lecture.article, "This is the new article content")

    def test_instructor_can_delete_lecture(self):
        self.client.force_authenticate(self.instructor)
        response = self.client.delete(self.lecture_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # -------------------------
    # Validation Tests
    # -------------------------
    def test_cannot_create_video_lecture_without_video(self):
        """Test validation: video lecture must have video file"""
        self.client.force_authenticate(self.instructor)

        payload = {
            "title": "Invalid Video Lecture",
            "order": 4,
            "duration": 15,
            "content_type": "video",
            # Missing video file - should fail
        }
        response = self.client.post(self.lecture_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for the generic content error message
        self.assertIn('content', response.data)
        self.assertIn('You must provide either a video, article, or file for the lecture',
                      str(response.data['content']))

    def test_cannot_create_article_lecture_without_content(self):
        """Test validation: article lecture must have article content"""
        self.client.force_authenticate(self.instructor)

        payload = {
            "title": "Invalid Article Lecture",
            "order": 5,
            "duration": 0,
            "content_type": "article",
            # Missing article content - should fail
        }
        response = self.client.post(self.lecture_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for the generic content error message
        self.assertIn('content', response.data)
        self.assertIn('You must provide either a video, article, or file for the lecture',
                      str(response.data['content']))

    def test_cannot_create_video_lecture_with_zero_duration(self):
        """Test validation: video lecture must have duration > 0"""
        self.client.force_authenticate(self.instructor)

        video_file = SimpleUploadedFile(
            "test.mp4",
            b"content",
            content_type="video/mp4"
        )

        payload = {
            "title": "Invalid Duration Lecture",
            "order": 6,
            "duration": 0,  # Invalid for video
            "content_type": "video",
            "video": video_file
        }
        response = self.client.post(self.lecture_create_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration', response.data)

    def test_cannot_create_lecture_with_multiple_content_types(self):
        """Test validation: cannot provide multiple content types"""
        self.client.force_authenticate(self.instructor)

        video_file = SimpleUploadedFile(
            "test.mp4",
            b"content",
            content_type="video/mp4"
        )

        payload = {
            "title": "Multiple Content Lecture",
            "order": 7,
            "duration": 15,
            "content_type": "video",
            "video": video_file,
            "article": "This should not be here"  # Both video and article - should fail
        }
        response = self.client.post(self.lecture_create_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)
        self.assertIn('cannot provide multiple content types', str(response.data['content']).lower())
