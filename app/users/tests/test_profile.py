"""
Test for the Profile API
"""
# users/tests/test_profile.py
from django.test import TestCase
# from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from core.models import User


class UserProfileTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Testpass123@',
            name='name',
            bio='new bio',
        )
        self.token = Token.objects.create(user=self.user)
        self.profile_url = reverse('user:profile')

    def authenticate(self):
        """Helper method to set authentication header."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_profile_view_authenticated_user(self):
        """Test authenticated user can view their profile"""
        self.authenticate()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'email': 'test@example.com',
            'role': 'student',
        }

        self.assertEqual(self.user.email, expected_data['email'])
        self.assertEqual(self.user.role, expected_data['role'])

    def test_profile_view_unauthenticated_user(self):
        """Test unauthenticated user cannot view profile"""

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_authenticated_user(self):
        """Test authenticated user can update their profile"""
        self.authenticate()
        update_data = {
            'name': 'Updated',
            'bio': 'Changed',
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated')
        self.assertEqual(self.user.bio, 'Changed')

    def test_profile_update_partial(self):
        """Test partial profile update (only some fields)"""
        self.authenticate()
        update_data = {
            'bio': 'Just updating my bio'
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.bio, 'Just updating my bio')

class InstructorProfileTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Testpass123@',
            role='instructor'
        )
        self.token = Token.objects.create(user=self.user)
        self.profile_url = reverse('user:profile')

    def test_profile_view_authenticated_user(self):
        """Test authenticated instructor can view their profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'email': 'test@example.com',
            'role': 'instructor',
        }

        self.assertEqual(self.user.email, expected_data['email'])
        self.assertEqual(self.user.role, expected_data['role'])
