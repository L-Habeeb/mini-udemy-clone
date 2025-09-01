"""
Test for the User Registration API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status


REGISTER_USER_URL = reverse('user:register')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

def user_exist(email):
    """return if user was created"""
    return get_user_model().objects.filter(email=email).exists()


class PublicUserRegistrationTests(TestCase):
    """Test the public features of the User Registration API"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_user_registration_success(self):
        """Test successful user registration with valid data"""
        payload = {
            'email': 'test@example.com',
            'password': 'Password123!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotEqual(user.password, payload['password'])
        self.assertNotIn('password', res.data)

    def test_user_registration_missing_email(self):
        """Test error returned when email is missing"""
        payload = {
            'password': 'Password123!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_password(self):
        """Test error returned when password is missing"""
        payload = {
            'email': 'test@example.com',
        }

        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exist = user_exist(payload['email'])
        self.assertFalse(exist)

    def test_user_registration_role_student(self):
        """Test returned student as default role"""
        payload = {
            'email': 'test@example.com',
            'password': 'Password123!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.role, 'student')
        exist = user_exist(payload['email'])
        self.assertTrue(exist)

    def test_user_registration_invalid_email(self):
        """Test error returned for invalid email format"""
        payload = {
            'email': 'invalid-email-format',
            'password': 'SecurePassword123!',
            'role': 'student',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exist = user_exist(payload['email'])
        self.assertFalse(exist)

    def test_user_registration_with_duplicate_email(self):
        """Test error returned if email already exists"""
        user_details = {
            'email': 'existing@example.com',
            'password': 'ExistingPassword123!',
            'name': 'first_user',
        }
        create_user(**user_details)
        payload = {
            'email': 'existing@example.com',
            'password': 'DifferentPassword123!',
            'name': 'second_user',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        users_with_email = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertEqual(users_with_email.count(), 1)
        self.assertEqual(users_with_email.first().name, 'first_user')

    def test_user_registration_role_assignment_student(self):
        """Test user registration with student role"""
        payload = {
            'email': 'student@example.com',
            'password': 'SecurePassword123!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.role, 'student')

    def test_user_registration_password_not_in_response(self):
        """Test that password is not returned in response data"""
        payload = {
            'email': 'secure@example.com',
            'password': 'SecurePassword123!',
            'name': 'Secure',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', res.data)

    def test_user_registration_case_insensitive_email(self):
        """Test that email is normalize"""
        create_user(
            email='test@EXAMPLE.COM',
            password='Password123!',
            name='First',
        )

        payload = {
            'email': 'test@example.com',
            'password': 'DifferentPassword123!',
            'name': 'Second',
        }

        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.get(email='test@example.com')
        self.assertEqual(user.name, 'First')

    def test_user_registration_empty_string_fields(self):
        """Test error returned for empty string fields"""
        payload = {
            'email': '',
            'password': '',
            'name': ''
        }

        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test error returned if password is less than 8 characters"""
        payload = {
            'email': 'shortpass@example.com',
            'password': 'Ab1!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist(payload['email']))

    def test_password_missing_uppercase(self):
        """Test error returned if password has no uppercase letter"""
        payload = {
            'email': 'noupper@example.com',
            'password': 'validpass1!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist(payload['email']))

    def test_password_missing_lowercase(self):
        """Test error returned if password has no lowercase letter"""
        payload = {
            'email': 'nolower@example.com',
            'password': 'VALIDPASS1!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist(payload['email']))

    def test_password_missing_digit(self):
        """Test error returned if password has no digit"""
        payload = {
            'email': 'nodigit@example.com',
            'password': 'ValidPass!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist(payload['email']))

    def test_password_missing_special_char(self):
        """Test error returned if password has no special character"""
        payload = {
            'email': 'nospecial@example.com',
            'password': 'ValidPass1',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist(payload['email']))

    def test_password_valid(self):
        """Test password passes all validation rules"""
        payload = {
            'email': 'valid@example.com',
            'password': 'ValidPass1!',
        }
        res = self.client.post(REGISTER_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user_exist(payload['email']))
