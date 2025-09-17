"""
Test for Cart API
"""
from decimal import Decimal

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.urls import reverse

from core.models import User, Course, Category, SubCategory, Enrollment, Cart


class CartAPITests(APITestCase):
    def setUp(self):
        """Set up test data for API tests"""
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            role='instructor'
        )
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            role='student'
        )

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            name='Python',
            description='Python programming',
            category=self.category
        )
        self.course1 = Course.objects.create(
            title='Django Mastery',
            description='Learn Django framework',
            price=Decimal('99.99'),
            category=self.category
        )
        self.course1.instructor.add(self.instructor)
        self.course1.subcategory.add(self.subcategory)

        self.course2 = Course.objects.create(
            title='React Fundamentals',
            description='Learn React',
            price=Decimal('79.99'),
            category=self.category
        )
        self.course2.instructor.add(self.instructor)
        self.course2.subcategory.add(self.subcategory)

        self.student_token = Token.objects.create(user=self.student)
        self.instructor_token = Token.objects.create(user=self.instructor)
        self.student2_token = Token.objects.create(user=self.student2)

    def test_add_course_to_cart_success(self):
        """Test successfully adding a course to cart"""
        url = reverse('course:cart-add', kwargs={'course_id': self.course1.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cart.objects.filter(student=self.student, course=self.course1).exists())
        self.assertEqual(response.data['course'], self.course1.id)

    def test_add_course_to_cart_unauthenticated(self):
        """Test adding course to cart without authentication"""
        url = reverse('course:cart-add', kwargs={'course_id': self.course1.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_nonexistent_course_to_cart(self):
        """Test adding non-existent course to cart"""
        url = reverse('course:cart-add', kwargs={'course_id': 99999})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_duplicate_course_to_cart(self):
        """Test adding same course twice to cart"""
        Cart.objects.create(student=self.student, course=self.course1)

        url = reverse('course:cart-add', kwargs={'course_id': self.course1.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.post(url)


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_enrolled_course_to_cart(self):
        """Test adding already enrolled course to cart"""
        Enrollment.objects.create(student=self.student, course=self.course1, is_active=True)

        url = reverse('course:cart-add', kwargs={'course_id': self.course1.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.post(url)


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_course_from_cart_success(self):
        """Test successfully removing course from cart"""
        Cart.objects.create(student=self.student, course=self.course1)

        url = reverse('course:cart-remove', kwargs={'course_id': self.course1.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.filter(student=self.student, course=self.course1).exists())

    def test_get_my_cart_empty(self):
        """Test getting empty cart"""
        url = reverse('course:my-cart')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)

    def test_get_my_cart_with_items(self):
        """Test getting cart with items"""
        Cart.objects.create(student=self.student, course=self.course1)
        Cart.objects.create(student=self.student, course=self.course2)

        url = reverse('course:my-cart')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], '179.98')
        self.assertEqual(response.data['total_items'], 2)
