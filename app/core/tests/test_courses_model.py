"""
Test for Course Models
"""
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from core.models import User, Course


class CourseModelTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='Testpass123@',
            name='Test Instructor',
            role='instructor'
        )

        self.student = User.objects.create_user(
            email='student@example.com',
            password='Testpass123@',
            name='Test Student',
            role='student'
        )

    def test_create_course_with_valid_data(self):
        """Test creating a course with all valid data"""
        course = Course.objects.create(
            title='Complete Python Bootcamp',
            description='Learn Python from beginner to advanced level',
            price=Decimal('99.99'),
            language='English',
            level='beginner'
        )
        course.instructor.set([self.instructor])

        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(course.title, 'Complete Python Bootcamp')
        self.assertIn(self.instructor, course.instructor.all())
        self.assertEqual(course.price, Decimal('99.99'))
        self.assertEqual(course.language, 'English')
        self.assertEqual(course.level, 'beginner')

        self.assertIsNotNone(course.created_at)
        self.assertIsNotNone(course.updated_at)

    def test_course_string_representation(self):
        """Test the __str__ method of Course model"""
        course = Course.objects.create(
            title='Django Masterclass',
            description='Master Django framework',
            price=Decimal('149.99'),
            language='English',
            level='intermediate'
        )
        course.instructor.set([self.instructor])

        self.assertEqual(str(course), 'Django Masterclass')

    def test_course_title_required(self):
        """Test that course title is required"""
        with self.assertRaises((ValidationError, IntegrityError)):
            course = Course(
                description='Some description',
                price=Decimal('99.99'),
                language='English',
                level='beginner'
            )
            course.save()
            course.instructor.set([self.instructor])
            course.full_clean()

    # def test_course_instructor_required(self):
    #     """Test that course must have an instructor"""
    #     with self.assertRaises(IntegrityError):
    #         Course.objects.create(
    #             title='Test Course',
    #             description='Test description',
    #             # instructor=None,
    #             price=Decimal('99.99'),
    #             language='English',
    #             level='beginner'
    #         )
    # def test_course_instructor_required(self):
    #     """Test that course must have an instructor"""
    #     with self.assertRaises(IntegrityError):
    #         Course.objects.create(
    #             # title='Test Course',
    #             description='Test description',
    #             price=Decimal('99.99'),
    #             language='English',
    #             level='beginner'
    #         )
    #         Course.full_clean(self)


    def test_course_level_choices(self):
        """Test that course level accepts only valid choices"""
        valid_levels = ['beginner', 'intermediate', 'advanced', 'all_levels']

        for level in valid_levels:
            course = Course.objects.create(
                title=f'Course {level}',
                description='Test description',
                price=Decimal('99.99'),
                language='English',
                level=level
            )
            course.instructor.set([self.instructor])
            self.assertEqual(course.level, level)

        with self.assertRaises(ValidationError):
            course = Course(
                title='Invalid Level Course',
                description='Test description',
                price=Decimal('99.99'),
                language='English',
                level='expert'
            )
            course.save()
            course.instructor.set([self.instructor])
            course.full_clean()

    def test_multiple_courses_same_instructor(self):
        """Test that one instructor can have multiple courses"""
        course1 = Course.objects.create(
            title='Python Basics',
            description='Learn Python fundamentals',
            price=Decimal('49.99'),
            language='English',
            level='beginner'
        )
        course1.instructor.set([self.instructor])

        course2 = Course.objects.create(
            title='Advanced Python',
            description='Master advanced Python concepts',
            price=Decimal('99.99'),
            language='English',
            level='advanced'
        )
        course2.instructor.set([self.instructor])

        self.assertEqual(Course.objects.count(), 2)
        self.assertIn(self.instructor, course1.instructor.all())
        self.assertIn(self.instructor, course2.instructor.all())

    def test_multiple_courses_multiple_instructor(self):
        """Test that two or more instructor can a courses"""
        instructor_2 = User.objects.create_user(
            email='instructor2@example.com',
            password='Testpass123@',
            name='Test Instructor2',
            role='instructor'
        )

        course = Course.objects.create(
            title='Python Basics',
            description='Learn Python fundamentals',
            price=Decimal('49.99'),
            language='English',
            level='beginner'
        )
        course.instructor.set([self.instructor, instructor_2])
        self.assertCountEqual([self.instructor, instructor_2], course.instructor.all())















# """
# Test for Course Management API
# """
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework import status
# from rest_framework.authtoken.models import Token
#
# from core.models import User, Course
#
#
# class CourseCreationTestCase(TestCase):
#     def setUp(self):
#         """Set up test data"""
#         self.client = APIClient()
#
#         self.student = User.objects.create_user(
#             email='student@example.com',
#             password='Testpass123@',
#             name='Student User',
#             role='student'
#         )
#
#         self.instructor = User.objects.create_user(
#             email='instructor@example.com',
#             password='Testpass123@',
#             name='Instructor User',
#             role='instructor'
#         )
#
#         self.student_token = Token.objects.create(user=self.student)
#         self.instructor_token = Token.objects.create(user=self.instructor)
#
#         self.courses_url = reverse('course:courses')
#
#         self.valid_course_data = {
#             'title': 'Complete Python Bootcamp',
#             'description': 'Learn Python from beginner to advanced level',
#             'price': '99.99',
#             'language': 'English',
#             'level': 'beginner'
#         }
#
#     def authenticate_student(self):
#         """Helper to authenticate as student"""
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.student_token.key}")
#
#     def authenticate_instructor(self):
#         """Helper to authenticate as instructor"""
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.instructor_token.key}")
#
#     def test_instructor_can_create_course(self):
#         """
#         Test that instructor can successfully create a course
#         Expected: 201 CREATED
#         """
#         self.authenticate_instructor()
#
#         response = self.client.post(self.courses_url, self.valid_course_data, format='json')
#
#         # Assert response status 201 CREATED
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#         # Assert course exists in database
#         self.assertEqual(Course.objects.count(), 1)
#
#         # Assert course details are correct
#         course = Course.objects.first()
#         self.assertEqual(course.title, self.valid_course_data['title'])
#         self.assertEqual(course.instructor, self.instructor)
#         self.assertEqual(str(course.price), self.valid_course_data['price'])
#
#         # Assert response contains course data
#         self.assertEqual(response.data['title'], self.valid_course_data['title'])
#         self.assertEqual(response.data['instructor']['id'], self.instructor.id)
#
#     def test_student_cannot_create_course(self):
#         """
#         Test that student cannot create a course
#         Expected: 403 FORBIDDEN
#         """
#         self.authenticate_student()
#
#         response = self.client.post(self.courses_url, self.valid_course_data, format='json')
#
#         # Assert response status 403 FORBIDDEN
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#         # Assert no course was created
#         self.assertEqual(Course.objects.count(), 0)
#
#     def test_unauthenticated_user_cannot_create_course(self):
#         """
#         Test that unauthenticated user cannot create course
#         Expected: 401 UNAUTHORIZED
#         """
#         # No authentication
#         response = self.client.post(self.courses_url, self.valid_course_data, format='json')
#
#         # Assert response status 401 UNAUTHORIZED
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         # Assert no course was created
#         self.assertEqual(Course.objects.count(), 0)
#
#     def test_create_course_invalid_data(self):
#         """
#         Test creating course with invalid data
#         Expected: 400 BAD REQUEST
#         """
#         self.authenticate_instructor()
#
#         invalid_data = {
#             'title': '',  # Empty title
#             'description': 'Valid description',
#             'price': 'invalid_price',  # Invalid price format
#             'language': 'English',
#             'level': 'invalid_level'  # Invalid level choice
#         }
#
#         response = self.client.post(self.courses_url, invalid_data, format='json')
#
#         # Assert response status 400 BAD REQUEST
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#         # Assert no course was created
#         self.assertEqual(Course.objects.count(), 0)
#
#         # Assert error details are returned
#         self.assertIn('title', response.data)
#         self.assertIn('price', response.data)
#         self.assertIn('level', response.data)
#
#     def test_create_course_missing_required_fields(self):
#         """
#         Test creating course with missing required fields
#         Expected: 400 BAD REQUEST
#         """
#         self.authenticate_instructor()
#
#         incomplete_data = {
#             'title': 'Python Course'
#             # Missing description, price, etc.
#         }
#
#         response = self.client.post(self.courses_url, incomplete_data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(Course.objects.count(), 0)
#
#
# class CourseListingTestCase(TestCase):
#     def setUp(self):
#         """Set up test data with existing courses"""
#         self.client = APIClient()
#
#         # Create users
#         self.instructor1 = User.objects.create_user(
#             email='instructor1@example.com',
#             password='Testpass123@',
#             name='Instructor One',
#             role='instructor'
#         )
#
#         self.instructor2 = User.objects.create_user(
#             email='instructor2@example.com',
#             password='Testpass123@',
#             name='Instructor Two',
#             role='instructor'
#         )
#
#         self.student = User.objects.create_user(
#             email='student@example.com',
#             password='Testpass123@',
#             name='Student',
#             role='student'
#         )
#
#         # Create courses
#         self.course1 = Course.objects.create(
#             title='Python Basics',
#             description='Learn Python fundamentals',
#             instructor=self.instructor1,
#             price='49.99',
#             language='English',
#             level='beginner'
#         )
#
#         self.course2 = Course.objects.create(
#             title='Advanced Django',
#             description='Master Django framework',
#             instructor=self.instructor2,
#             price='99.99',
#             language='English',
#             level='advanced'
#         )
#
#         self.courses_url = reverse('course:courses')
#
#     def test_anyone_can_list_courses(self):
#         """
#         Test that anyone (authenticated or not) can view course list
#         Expected: 200 OK with course data
#         """
#         # Test without authentication
#         response = self.client.get(self.courses_url)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 2)
#
#         # Check course data is included
#         course_titles = [course['title'] for course in response.data['results']]
#         self.assertIn('Python Basics', course_titles)
#         self.assertIn('Advanced Django', course_titles)
#
#     def test_course_list_includes_instructor_info(self):
#         """
#         Test that course list includes instructor information
#         Expected: Each course has instructor details
#         """
#         response = self.client.get(self.courses_url)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # Check first course has instructor info
#         first_course = response.data['results'][0]
#         self.assertIn('instructor', first_course)
#         self.assertIn('name', first_course['instructor'])
#         self.assertIn('email', first_course['instructor'])
#
#     def test_instructor_can_list_own_courses(self):
#         """
#         Test that instructor can filter their own courses
#         Expected: Only instructor's courses returned
#         """
#         token = Token.objects.create(user=self.instructor1)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
#
#         # Add query parameter to get own courses
#         response = self.client.get(f"{self.courses_url}?my_courses=true")
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)
#         self.assertEqual(response.data['results'][0]['title'], 'Python Basics')
#
#
# class CourseDetailTestCase(TestCase):
#     def setUp(self):
#         """Set up test data"""
#         self.client = APIClient()
#
#         self.instructor = User.objects.create_user(
#             email='instructor@example.com',
#             password='Testpass123@',
#             name='Instructor',
#             role='instructor'
#         )
#
#         self.other_instructor = User.objects.create_user(
#             email='other@example.com',
#             password='Testpass123@',
#             name='Other Instructor',
#             role='instructor'
#         )
#
#         self.course = Course.objects.create(
#             title='Python Course',
#             description='Learn Python',
#             instructor=self.instructor,
#             price='49.99',
#             language='English',
#             level='beginner'
#         )
#
#         self.instructor_token = Token.objects.create(user=self.instructor)
#         self.other_token = Token.objects.create(user=self.other_instructor)
#
#         self.course_detail_url = reverse('course:course-detail', kwargs={'pk': self.course.pk})
#
#     def test_anyone_can_view_course_detail(self):
#         """
#         Test that anyone can view course details
#         Expected: 200 OK with full course info
#         """
#         response = self.client.get(self.course_detail_url)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], 'Python Course')
#         self.assertEqual(response.data['instructor']['id'], self.instructor.id)
#
#     def test_instructor_can_update_own_course(self):
#         """
#         Test that instructor can update their own course
#         Expected: 200 OK with updated data
#         """
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.instructor_token.key}")
#
#         update_data = {
#             'title': 'Updated Python Course',
#             'price': '59.99'
#         }
#
#         response = self.client.patch(self.course_detail_url, update_data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # Check course is updated in database
#         self.course.refresh_from_db()
#         self.assertEqual(self.course.title, 'Updated Python Course')
#         self.assertEqual(str(self.course.price), '59.99')
#
#     def test_instructor_cannot_update_other_course(self):
#         """
#         Test that instructor cannot update another instructor's course
#         Expected: 403 FORBIDDEN
#         """
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.other_token.key}")
#
#         update_data = {
#             'title': 'Hacked Course Title'
#         }
#
#         response = self.client.patch(self.course_detail_url, update_data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#         # Check course is not updated
#         self.course.refresh_from_db()
#         self.assertEqual(self.course.title, 'Python Course')  # Original title