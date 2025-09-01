"""
Test for the User Login
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('user:login')
        self.email = "test@example.com"
        self.password = "Testpass123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

    def test_user_can_login_and_get_token(self):
        """Valid login should return a token."""
        response = self.client.post(self.login_url, {
            "username": self.email,
            "password": self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_fails_with_invalid_credentials(self):
        """Invalid login should return error 400."""
        response = self.client.post(self.login_url, {
            "username": self.email,
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_token_is_not_regenerated_on_multiple_logins(self):
        """Token should remain same for repeated logins."""
        # First login
        response1 = self.client.post(self.login_url, {
            "username": self.email,
            "password": self.password
        })
        token1 = response1.data['token']

        # Second login
        response2 = self.client.post(self.login_url, {
            "username": self.email,
            "password": self.password
        })
        token2 = response2.data['token']

        self.assertEqual(token1, token2)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)
