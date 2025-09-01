"""
Test for becoming an instructor API
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class BecomeInstructorTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='student@example.com',
            password='Testpass123@',
            name='Test User',
            role='student'
        )
        self.token = Token.objects.create(user=self.user)
        self.become_instructor_url = reverse('user:become-instructor')

    def authenticate(self):
        """Helper method to authenticate user"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_student_can_become_instructor(self):
        """Test that a student can successfully become an instructor"""
        self.authenticate()

        self.assertEqual(self.user.role, 'student')
        response = self.client.post(self.become_instructor_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Successfully became an instructor!')
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'instructor')
        self.assertEqual(response.data['Instructor-Profile'].get('role'), 'instructor')

    def test_instructor_cannot_become_instructor_again(self):
        """Test that an existing instructor cannot become instructor again"""
        self.authenticate()
        self.client.post(self.become_instructor_url)
        response = self.client.post(self.become_instructor_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('error', response.data)
        # self.assertEqual(response.data['error'], 'You are already an instructor')

    def test_unauthenticated_user_cannot_become_instructor(self):
        """
        Test that unauthenticated user cannot become instructor
        """
        response = self.client.post(self.become_instructor_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_become_instructor_with_additional_info(self):
        """Test becoming instructor with optional bio update"""
        self.authenticate()
        instructor_data = {
            'bio': 'Experienced developer ready to teach'
        }
        response = self.client.post(self.become_instructor_url, instructor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'instructor')
        self.assertEqual(self.user.bio, instructor_data['bio'])
