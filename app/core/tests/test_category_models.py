"""
Category Model Test
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
# from django.db import IntegrityError
# from django.db.utils import DataError
# import uuid

from core.models import Category


class CategoryModelTests(TestCase):
    """
    Test suite for Category model - Foundation test for Categories & SubCategories system
    """

    def setUp(self):
        """Set up test data for each test method"""
        self.valid_category_data = {
            'name': 'Technology',
            'description': 'All technology-related courses and content',
            'slug': 'technology'
        }

    def test_category_creation_with_valid_data(self):
        """Test creating a category with all valid required fields"""
        category = Category.objects.create(**self.valid_category_data)

        self.assertIsInstance(category, Category)
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.description, 'All technology-related courses and content')
        self.assertEqual(category.slug, 'technology')

    def test_category_creation_minimal_required_fields(self):
        """Test creating category with only required fields (name and slug)"""
        minimal_data = {
            'name': 'Business',
            'slug': 'business'
        }
        category = Category.objects.create(**minimal_data)

        self.assertEqual(category.name, 'Business')
        self.assertEqual(category.slug, 'business')
        self.assertEqual(category.description, '')
        self.assertTrue(Category.objects.filter(name='Business').exists())

    def test_category_name_required(self):
        """Test that name field is required"""
        category = Category(slug='test-slug')
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_category_slug_required(self):
        """Test that slug field is required"""
        category = Category(name='Test Category')
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_category_string_representation(self):
        """Test the __str__ method returns the category name"""
        category = Category.objects.create(name='Creative Arts', slug='creative-arts')

        self.assertEqual(str(category), 'Creative Arts')
        self.assertEqual(category.__str__(), 'Creative Arts')

    def test_category_string_representation_with_special_characters(self):
        """Test string representation with special characters"""
        category = Category.objects.create(
            name='Health & Wellness',
            slug='health-wellness'
        )

        self.assertEqual(str(category), 'Health & Wellness')

    def test_category_empty_string_fields(self):
        """Test behavior with empty string values"""
        category = Category(name='', slug='test')
        with self.assertRaises(ValidationError):
            category.full_clean()

        category = Category(name='Test', slug='test', description='')
        self.assertEqual(category.description, '')

    def test_category_unicode_support(self):
        """Test category names with unicode characters"""
        unicode_categories = [
            ('Développement Web', 'dev-web'),
            ('Programación', 'programacion'),
            ('デザイン', 'design-jp'),
            ('Мода и стиль', 'fashion-ru'),
        ]

        for name, slug in unicode_categories:
            with self.subTest(name=name):
                category = Category.objects.create(name=name, slug=slug)
                self.assertEqual(category.name, name)
                self.assertTrue(Category.objects.filter(name=name).exists())

    def test_bulk_category_creation(self):
        """Test creating multiple categories efficiently"""
        categories_data = [
            Category(name='Technology', slug='technology'),
            Category(name='Business', slug='business'),
            Category(name='Arts', slug='arts'),
            Category(name='Health', slug='health'),
            Category(name='Language', slug='language'),
        ]
        created_categories = Category.objects.bulk_create(categories_data)
        self.assertEqual(len(created_categories), 5)
        self.assertEqual(Category.objects.count(), 5)

        for cat_data in categories_data:
            self.assertTrue(
                Category.objects.filter(name=cat_data.name).exists()
            )

    def test_category_filtering_performance(self):
        """Test efficient filtering operations"""
        self.test_bulk_category_creation()

        tech_categories = Category.objects.filter(name__icontains='tech')
        self.assertTrue(tech_categories.exists())
