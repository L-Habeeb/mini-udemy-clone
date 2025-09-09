"""Enrollment API Test"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.models import Course, Category, Enrollment, SubCategory, Enrollment

User = get_user_model()


class EnrollmentViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.student = User.objects.create_user(
            email='student@test.com',
            password='Testpass123!'
        )
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='Testpass123!'
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='Testpass123!',
            role='instructor',
        )

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Web Development',
            description='Learn Web Dev'
        )

        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            category=self.category,
            price=99.99
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)


    def test_enroll_in_course_success(self):
        """Test successful course enrollment"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:enroll', kwargs={'course_id': self.course.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student'], self.student.id)
        self.assertEqual(response.data['course'], self.course.id)
        self.assertEqual(response.data['course_title'], 'Python Basics')

        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )

    def test_enroll_in_course_unauthenticated(self):
        """Test enrollment requires authentication"""
        url = reverse('course:enroll', kwargs={'course_id': self.course.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enroll_in_course_duplicate(self):
        """Test duplicate enrollment prevention"""
        Enrollment.objects.create(student=self.student, course=self.course)

        self.client.force_authenticate(user=self.student)
        url = reverse('course:enroll', kwargs={'course_id': self.course.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Enrollment with this Student and Course already exists.',
            str(response.data)
        )

    def test_enroll_in_nonexistent_course(self):
        """Test enrollment in non-existent course"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:enroll', kwargs={'course_id': 99999})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No Course matches', str(response.data))


    def test_instructor_can_enroll(self):
        """Test instructors can enroll as students"""
        self.client.force_authenticate(user=self.instructor)
        url = reverse('course:enroll', kwargs={'course_id': self.course.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student'], self.instructor.id)

        self.assertTrue(
            Enrollment.objects.filter(student=self.instructor, course=self.course).exists()
        )

    def test_my_enrollments_empty(self):
        """Test empty enrollments list"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:my-enrollments')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_my_enrollments_with_data(self):
        """Test enrollments list with data"""
        enrollment_1 = Enrollment.objects.create(student=self.student, course=self.course)

        course2 = Course.objects.create(
            title='Django Basics',
            description='Learn Django',
            category=self.category,
            price=149.99
        )
        course2.instructor.add(self.instructor)
        course2.subcategory.add(self.subcategory)
        enrollment_2 = Enrollment.objects.create(student=self.student, course=course2)

        self.client.force_authenticate(user=self.student)
        url = reverse('course:my-enrollments')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        enrollment_data = response.data['results']
        self.assertEqual(enrollment_data[0]['course_title'], 'Django Basics')

    def test_my_enrollments_unauthenticated(self):
        """Test my enrollments requires authentication"""
        url = reverse('course:my-enrollments')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EnrollmentIntegrationTests(APITestCase):
    """
    Integration tests for the complete enrollment workflow
    """

    def setUp(self):
        self.client = APIClient()

        self.student = User.objects.create_user(
            email='student@test.com',
            password='Testpass123!',
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='Testpass123!',
            role='instructor',
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Web Dev',
            description='Learn Web Dev'
        )

        self.course1 = Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            category=self.category,
            price=99.99
        )
        self.course1.instructor.add(self.instructor)
        self.course1.subcategory.add(self.subcategory)

        self.course2 = Course.objects.create(
            title='Django Advanced',
            description='Advanced Django concepts',
            category=self.category,
            price=199.99
        )
        self.course2.instructor.add(self.instructor)
        self.course2.subcategory.add(self.subcategory)

    def test_complete_enrollment_workflow(self):
        """Test the complete enrollment workflow from start to finish"""
        self.client.force_authenticate(user=self.student)

        stats_url = reverse('course:course-enrollment-stats', kwargs={'course_id': self.course1.id})
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_enrollments'], 0)

        my_enrollments_url = reverse('course:my-enrollments')
        response = self.client.get(my_enrollments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        enroll_url1 = reverse('course:enroll', kwargs={'course_id': self.course1.id})
        response = self.client.post(enroll_url1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course_title'], 'Python Basics')
        enrollment1_id = response.data['id']

        response = self.client.get(stats_url)
        self.assertEqual(response.data['total_enrollments'], 1)

        response = self.client.get(my_enrollments_url)
        self.assertEqual(response.data['results'][0]['course_title'], 'Python Basics')
        self.assertEqual(response.data['count'], 1)

        enroll_url2 = reverse('course:enroll', kwargs={'course_id': self.course2.id})
        response = self.client.post(enroll_url2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course_title'], 'Django Advanced')

        response = self.client.get(my_enrollments_url)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(response.data['results'][0]['course_title'], 'Django Advanced')
        self.assertEqual(response.data['results'][1]['course_title'], 'Python Basics')

        response = self.client.post(enroll_url1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Enrollment.objects.filter(student=self.student).count(), 2)

    def test_multiple_students_same_course(self):
        """Test multiple students enrolling in the same course"""
        student2 = User.objects.create_user(
            email='student2@test.com',
            password='Testpass123!'
        )

        enroll_url = reverse('course:enroll', kwargs={'course_id': self.course1.id})

        # Student 1 enrolls
        self.client.force_authenticate(user=self.student)
        response = self.client.post(enroll_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Student 2 enrolls
        self.client.force_authenticate(user=student2)
        response = self.client.post(enroll_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check enrollment stats
        stats_url = reverse('course:course-enrollment-stats', kwargs={'course_id': self.course1.id})
        response = self.client.get(stats_url)
        self.assertEqual(response.data['total_enrollments'], 2)

        # Each student sees only their own enrollment
        self.client.force_authenticate(user=self.student)
        my_enrollments_url = reverse('course:my-enrollments')
        response = self.client.get(my_enrollments_url)
        self.assertEqual(response.data['count'], 1)

        self.client.force_authenticate(user=student2)
        response = self.client.get(my_enrollments_url)
        self.assertEqual(response.data['count'], 1)


    def test_public_access_to_enrollment_stats(self):
        """Test that enrollment stats are publicly accessible"""
        # Create some enrollments
        Enrollment.objects.create(student=self.student, course=self.course1)
        Enrollment.objects.create(student=self.instructor, course=self.course1)

        # Access stats without authentication
        stats_url = reverse('course:course-enrollment-stats', kwargs={'course_id': self.course1.id})
        response = self.client.get(stats_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_enrollments'], 2)
        self.assertEqual(response.data['course_title'], 'Python Basics')
