"""
Tests for the User model and its validations.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core import models

User = get_user_model()


class BaseModelTest(TestCase):
    """Base test class with common setup"""
    
    @classmethod
    def setUpTestData(cls):
        cls.normal_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123',
        )
        
        cls.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
        )


class ModelValidationTests(TestCase):
    """Test model validations and constraints"""
    
    def test_user_email_unique_constraint(self):
        """Test that email must be unique"""
        User.objects.create_user(
            email='unique@example.com',
            password='test123'
        )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='unique@example.com',
                password='test123'
            )
    
    def test_invalid_email_validation(self):
        """Test validation for invalid email format"""
        user = User(
            email='invalid-email',
            password='test123'
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_required_field_validation(self):
        """Test that required fields are enforced"""
        user = User()  # Missing required fields
        
        with self.assertRaises(ValidationError):
            user.full_clean()


class UserModelTests(TestCase):
    def test_create_student_user(self):
        """Test creating a student user"""
        user = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.assertEqual(user.role, 'student')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_instructor_user(self):
        """Test creating an instructor user"""
        user = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        self.assertEqual(user.role, 'instructor')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.role, 'admin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
