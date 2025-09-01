"""
Test for Course Management API
"""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from core.models import Course, Category, SubCategory

User = get_user_model()


class CourseAPITestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='Testpass123@',
            name='Instructor User',
            role='instructor'
        )
        self.instructor2 = User.objects.create_user(
            email='instructor2@example.com',
            password='Testpass123@',
            name='Second Instructor',
            role='instructor'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='Testpass123@',
            name='Student User',
            role='student'
        )

        self.instructor_token = Token.objects.create(user=self.instructor)
        self.instructor2_token = Token.objects.create(user=self.instructor2)
        self.student_token = Token.objects.create(user=self.student)

        self.category = Category.objects.create(name='Development')
        self.subcategory1 = SubCategory.objects.create(category=self.category, name='Web Development')
        self.subcategory2 = SubCategory.objects.create(category=self.category, name='Mobile Development')

        self.courses_url = reverse('course:course-list')

        self.valid_course_data = {
            'category': 'Development',
            'subcategory': ['Web Development', 'Mobile Development'],
            'title': 'Python Full-Stack Development',
            'description': 'Learn Python and its frameworks',
            'objectives': ['Learn Python Basic', 'Learn DRF', 'Learn Data Analysis'],
            'instructor': ['instructor2@example.com'],
            'language': 'English',
            'level': 'Beginner',
            'price': '199.99'
        }

    def authenticate_instructor(self):
        """Helper to authenticate as instructor"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.instructor_token.key}")

    def authenticate_student(self):
        """Helper to authenticate as student"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.student_token.key}")

    def test_instructor_can_create_course(self):
        """Test instructor can create course with all required fields"""
        self.authenticate_instructor()

        response = self.client.post(self.courses_url, self.valid_course_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

        course = Course.objects.first()
        self.assertEqual(course.title, self.valid_course_data['title'])
        self.assertEqual(course.category.name, 'Development')
        self.assertEqual(course.subcategory.count(), 2)

    def test_student_cannot_create_course(self):
        """Test student cannot create course"""
        self.authenticate_student()

        response = self.client.post(self.courses_url, self.valid_course_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 0)

    def test_create_course_missing_required_fields(self):
        """Test creating course without required fields fails"""
        self.authenticate_instructor()

        incomplete_data = {'title': 'Test Course'}
        response = self.client.post(self.courses_url, incomplete_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 0)

    def test_create_course_invalid_instructor_role(self):
        """Test creating course with non-instructor user fails"""
        self.authenticate_instructor()

        invalid_data = self.valid_course_data.copy()
        invalid_data['instructor'] = ['student@example.com']

        response = self.client.post(self.courses_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('instructor', response.data)

    def test_anyone_can_list_courses(self):
        """Test anyone can view course list"""
        course = Course.objects.create(
            category=self.category,
            title='Test Course',
            description='Test description',
            price=Decimal('99.99'),
            language='English',
            level='Beginner'
        )
        course.instructor.set([self.instructor])
        course.subcategory.set([self.subcategory1])

        response = self.client.get(self.courses_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_course_detail_view(self):
        """Test retrieving course details"""
        course = Course.objects.create(
            category=self.category,
            title='Detail Test Course',
            description='Test description',
            price=Decimal('99.99'),
            language='English',
            level='Beginner'
        )
        course.instructor.set([self.instructor])
        course.subcategory.set([self.subcategory1])

        detail_url = reverse('course:course-detail', kwargs={'pk': course.pk})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail Test Course')
        self.assertIn('instructor', response.data)

    def test_instructor_can_update_own_course(self):
        """Test instructor can update their own course"""
        course = Course.objects.create(
            category=self.category,
            title='Original Title',
            description='Test description',
            price=Decimal('99.99'),
            language='English',
            level='Beginner'
        )
        course.instructor.set([self.instructor])
        course.subcategory.set([self.subcategory1])

        self.authenticate_instructor()
        detail_url = reverse('course:course-detail', kwargs={'pk': course.pk})

        update_data = {
            'title': 'Updated Title',
            'price': '149.99'
        }
        response = self.client.patch(detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Updated Title')

    def test_instructor_cannot_update_other_course(self):
        """Test instructor cannot update another instructor's course"""
        course = Course.objects.create(
            category=self.category,
            title='Other Course',
            description='Test description',
            price=Decimal('99.99'),
            language='English',
            level='Beginner'
        )
        course.instructor.set([self.instructor2])
        course.subcategory.set([self.subcategory1])

        self.authenticate_instructor()
        detail_url = reverse('course:course-detail', kwargs={'pk': course.pk})

        update_data = {'title': 'Hacked Title'}
        response = self.client.patch(detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Other Course')

    def test_instructor_can_delete_own_course(self):
        """Test instructor can delete their own course"""
        course = Course.objects.create(
            category=self.category,
            title='To Delete',
            description='Test description',
            price=Decimal('99.99'),
            language='English',
            level='Beginner'
        )
        course.instructor.set([self.instructor])
        course.subcategory.set([self.subcategory1])

        self.authenticate_instructor()
        detail_url = reverse('course:course-detail', kwargs={'pk': course.pk})

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)
