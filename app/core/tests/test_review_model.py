"""
Test for Review and Rating Model
"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Course, Category, Enrollment, CourseReview

User = get_user_model()


class CourseReviewModelTests(TestCase):
    def setUp(self):
        """Set up test data for CourseReview model tests"""
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            role='instructor'
        )

        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
        )

        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
        )

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )

        self.course = Course.objects.create(
            title='Django Mastery',
            description='Learn Django',
            category=self.category,
            price=99.99
        )
        self.course.instructor.add(self.instructor)

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_valid_review_creation(self):
        """Test creating a valid course review"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Excellent course! Highly recommended.'
        )

        self.assertEqual(review.student, self.student)
        self.assertEqual(review.course, self.course)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, 'Excellent course! Highly recommended.')
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_review_string_representation(self):
        """Test CourseReview __str__ method"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=4,
            review_text='Good course'
        )

        expected_str = f"{self.student.email} - {self.course.title} (4/5)"
        self.assertEqual(str(review), expected_str)

    def test_rating_validation_within_range(self):
        """Test that ratings 1-5 are valid"""
        for rating in [1, 2, 3, 4, 5]:
            with self.subTest(rating=rating):
                review = CourseReview(
                    student=self.student,
                    course=self.course,
                    rating=rating,
                    review_text='Test review'
                )
                review.full_clean()

    def test_rating_validation_below_minimum(self):
        """Test that rating below 1 is invalid"""
        review = CourseReview(
            student=self.student,
            course=self.course,
            rating=0,
            review_text='Test review'
        )

        with self.assertRaises(ValidationError) as context:
            review.full_clean()

        self.assertIn('rating', context.exception.message_dict)

    def test_rating_validation_above_maximum(self):
        """Test that rating above 5 is invalid"""
        review = CourseReview(
            student=self.student,
            course=self.course,
            rating=6,
            review_text='Test review'
        )

        with self.assertRaises(ValidationError) as context:
            review.full_clean()

        self.assertIn('rating', context.exception.message_dict)
    def test_different_students_can_review_same_course(self):
        """Test that different students can review the same course"""
        Enrollment.objects.create(
            student=self.student2,
            course=self.course
        )

        review1 = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Great course!'
        )

        review2 = CourseReview.objects.create(
            student=self.student2,
            course=self.course,
            rating=4,
            review_text='Good course!'
        )

        self.assertEqual(CourseReview.objects.count(), 2)
        self.assertNotEqual(review1.student, review2.student)
        self.assertEqual(review1.course, review2.course)

    def test_same_student_can_review_different_courses(self):
        """Test that the same student can review multiple courses"""
        course2 = Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            category=self.category,
            price=49.99
        )
        course2.instructor.add(self.instructor)
        Enrollment.objects.create(
            student=self.student,
            course=course2
        )
        review1 = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Great Django course!'
        )
        review2 = CourseReview.objects.create(
            student=self.student,
            course=course2,
            rating=4,
            review_text='Good Python course!'
        )
        self.assertEqual(CourseReview.objects.count(), 2)
        self.assertEqual(review1.student, review2.student)
        self.assertNotEqual(review1.course, review2.course)

    def test_review_text_can_be_blank(self):
        """Test that review_text can be empty (rating-only review)"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text=''
        )

        self.assertEqual(review.review_text, '')
        review.full_clean()

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when review is updated"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Original review'
        )

        original_updated_at = review.updated_at

        # Small delay to ensure timestamp difference
        from time import sleep
        sleep(0.001)

        # Update the review
        review.review_text = 'Updated review'
        review.save()

        # Refresh from database
        review.refresh_from_db()

        self.assertGreater(review.updated_at, original_updated_at)
