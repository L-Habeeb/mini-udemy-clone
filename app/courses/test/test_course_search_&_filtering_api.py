"""
Test Search & Filtering API Endpoints
"""
from rest_framework.test import APITestCase
from decimal import Decimal
from django.urls import reverse

from core.models import (Category, SubCategory,
                         CourseReview, Course,
                         User, Enrollment)

class CourseSearchFilteringAPITest(APITestCase):
    """Test Course Search and Filtering API endpoints"""

    def setUp(self):
        """Set up test data for search and filtering"""
        self.programming_category = Category.objects.create(
            name="Programming",
            description="Programming courses"
        )
        self.design_category = Category.objects.create(
            name="Design",
            description="Design courses"
        )

        self.web_dev_subcategory = SubCategory.objects.create(
            category=self.programming_category,
            name="Web Development",
            description="Web development courses"
        )
        self.mobile_dev_subcategory = SubCategory.objects.create(
            category=self.programming_category,
            name="Mobile Development",
            description="Mobile app development"
        )
        self.ui_design_subcategory = SubCategory.objects.create(
            category=self.design_category,
            name="UI Design",
            description="User interface design"
        )

        self.instructor1 = User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password='Testpass123@',
            role="instructor"
        )
        self.instructor2 = User.objects.create_user(
            name="Jane Smith",
            email="jane@example.com",
            password='Testpass123@',
            role="instructor"
        )

        self.django_course = Course.objects.create(
            title="Complete Django Web Development",
            description="Learn Django framework from scratch to build amazing web applications",
            category=self.programming_category,
            language="English",
            level="Beginner",
            price=Decimal('49.99')
        )
        self.django_course.instructor.add(self.instructor1)
        self.django_course.subcategory.add(self.web_dev_subcategory)

        self.react_course = Course.objects.create(
            title="React Native Mobile App Development",
            description="Build cross-platform mobile apps with React Native and JavaScript",
            category=self.programming_category,
            language="English",
            level="Intermediate",
            price=Decimal('79.99')
        )
        self.react_course.instructor.add(self.instructor2)
        self.react_course.subcategory.add(self.mobile_dev_subcategory)

        self.python_course = Course.objects.create(
            title="Python Programming Fundamentals",
            description="Master Python programming language with hands-on projects",
            category=self.programming_category,
            language="English",
            level="Beginner",
            price=Decimal('29.99')
        )
        self.python_course.instructor.add(self.instructor1)
        self.python_course.subcategory.add(self.web_dev_subcategory)

        self.design_course = Course.objects.create(
            title="Modern UI Design Principles",
            description="Learn modern user interface design with Figma and Adobe XD",
            category=self.design_category,
            language="English",
            level="All-Level",
            price=Decimal('39.99')
        )
        self.design_course.instructor.add(self.instructor2)
        self.design_course.subcategory.add(self.ui_design_subcategory)

        student = User.objects.create_user(
            name="Test Student",
            email="student@example.com",
            password='Testpass123@',
            role="student"
        )
        Enrollment.objects.create(
            student=student,
            course=self.django_course
        )

        CourseReview.objects.create(
            student=student,
            course=self.django_course,
            rating=5,
            review_text="Excellent course!"
        )

        Enrollment.objects.create(
            student=student,
            course=self.python_course
        )

        CourseReview.objects.create(
            student=student,
            course=self.python_course,
            rating=3,
            review_text="Good course"
        )

    def test_search_by_course_title(self):
        """Test searching courses by title"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'q': 'Django'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Complete Django Web Development')

        # Search for "Python" in title
        response = self.client.get(url, {'q': 'Python'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Python Programming Fundamentals')

        # Case-insensitive search
        response = self.client.get(url, {'q': 'REACT'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'React Native Mobile App Development')

    def test_search_by_course_description(self):
        """Test searching courses by description"""
        url = reverse('course:course-search')

        # Search for "framework" in description
        response = self.client.get(url, {'q': 'framework'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Complete Django Web Development')

        # Search for "mobile" in description
        response = self.client.get(url, {'q': 'mobile'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'React Native Mobile App Development')

    def test_search_no_results(self):
        """Test search with no matching results"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 0)

    def test_search_empty_query(self):
        """Test search with empty query returns all courses"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'q': ''})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 4)

    def test_filter_by_category(self):
        """Test filtering courses by category name"""
        url = reverse('course:course-search')

        # Filter by "Programming" category
        response = self.client.get(url, {'category': 'Programming'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 3)  # Django, React, Python courses

        # Filter by "Design" category
        response = self.client.get(url, {'category': 'Design'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)  # Design course only
        self.assertEqual(results[0]['title'], 'Modern UI Design Principles')

    def test_filter_by_nonexistent_category(self):
        """Test filtering by non-existent category"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'category': 'NonExistent'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 0)

    def test_filter_by_subcategory(self):
        """Test filtering courses by subcategory name"""
        url = reverse('course:course-search')

        # Filter by "Web Development" subcategory
        response = self.client.get(url, {'subcategory': 'Web Development'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 2)  # Django and Python courses

        # Filter by "Mobile Development" subcategory
        response = self.client.get(url, {'subcategory': 'Mobile Development'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)  # React Native course
        self.assertEqual(results[0]['title'], 'React Native Mobile App Development')

    def test_filter_by_level(self):
        """Test filtering courses by level"""
        url = reverse('course:course-search')

        # Filter by "Beginner" level
        response = self.client.get(url, {'level': 'Beginner'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 2)  # Django and Python courses

        # Filter by "Intermediate" level
        response = self.client.get(url, {'level': 'Intermediate'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)  # React course
        self.assertEqual(results[0]['title'], 'React Native Mobile App Development')

    def test_filter_by_minimum_rating(self):
        """Test filtering courses by minimum rating"""
        url = reverse('course:course-search')

        # Filter courses with rating >= 4
        response = self.client.get(url, {'min_rating': 4})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Complete Django Web Development')

        # Filter courses with rating >= 3
        response = self.client.get(url, {'min_rating': 3})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 2)  # Django (5 stars) and Python (3 stars)

    def test_combined_text_search_and_category_filter(self):
        """Test combining text search with category filter"""
        url = reverse('course:course-search')

        # Search "Development" + Programming category
        response = self.client.get(url, {
            'q': 'Development',
            'category': 'Programming'
        })
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 2)  # Django and React courses

        # Search "Design" + Design category
        response = self.client.get(url, {
            'q': 'Design',
            'category': 'Design'
        })
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 1)  # Design course

    def test_combined_multiple_filters(self):
        """Test combining multiple filters"""
        url = reverse('course:course-search')

        # Programming + Beginner + Web Development
        response = self.client.get(url, {
            'category': 'Programming',
            'level': 'Beginner',
            'subcategory': 'Web Development'
        })
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 2)  # Django and Python courses

    def test_sort_by_rating(self):
        """Test sorting courses by rating (highest first)"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'sort': 'rating'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        # First course should have highest rating (Django with 5 stars)
        self.assertEqual(results[0]['title'], 'Complete Django Web Development')

    def test_sort_by_newest(self):
        """Test sorting courses by creation date (newest first)"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'sort': 'newest'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        self.assertEqual(len(results), 4)
        # Should be ordered by created_at desc (newest first)

    def test_sort_by_price_low_to_high(self):
        """Test sorting courses by price (low to high)"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'sort': 'price'})
        self.assertEqual(response.status_code, 200)

        results = response.json()['results']
        # First course should have lowest price (Python: 29.99)
        self.assertEqual(results[0]['title'], 'Python Programming Fundamentals')

    def test_search_pagination(self):
        """Test search results are paginated"""
        url = reverse('course:course-search')

        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
