"""
Test for Cart Model
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Course, Category, SubCategory, Cart, Enrollment

User = get_user_model()

class CartModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
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

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            name='Python',
            description='Python programming',
            category=self.category
        )
        self.course = Course.objects.create(
            title='Django Mastery',
            description='Learn Django framework',
            price=Decimal('99.99'),
            category=self.category
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)

    def test_cart_model_creation(self):
        """Test basic cart item creation"""
        cart_item = Cart.objects.create(
            student=self.student,
            course=self.course
        )

        self.assertEqual(cart_item.student, self.student)
        self.assertEqual(cart_item.course, self.course)
        self.assertIsNotNone(cart_item.added_at)

    def test_cart_unique_constraint(self):
        """Test that same course cannot be added twice by same student"""
        Cart.objects.create(student=self.student, course=self.course)

        with self.assertRaises(ValidationError):
            Cart.objects.create(student=self.student, course=self.course)

    def test_different_students_can_add_same_course(self):
        """Test that different students can add same course to cart"""
        student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            role='student'
        )

        cart1 = Cart.objects.create(student=self.student, course=self.course)
        cart2 = Cart.objects.create(student=student2, course=self.course)

        self.assertNotEqual(cart1, cart2)
        self.assertEqual(Cart.objects.count(), 2)

    def test_student_can_add_multiple_courses(self):
        """Test that student can add multiple different courses"""
        course2 = Course.objects.create(
            title='React Fundamentals',
            description='Learn React',
            price=Decimal('79.99'),
            category=self.category
        )
        course2.instructor.add(self.instructor)

        Cart.objects.create(student=self.student, course=self.course)
        Cart.objects.create(student=self.student, course=course2)

        self.assertEqual(Cart.objects.filter(student=self.student).count(), 2)

    def test_cart_deletion_cascade(self):
        """Test cart item deletion when student or course is deleted"""
        cart_item = Cart.objects.create(student=self.student, course=self.course)
        cart_id = cart_item.id

        self.course.delete()
        self.assertFalse(Cart.objects.filter(id=cart_id).exists())

    def test_cart_ordering(self):
        """Test cart items are ordered by added_at descending (newest first)"""
        course2 = Course.objects.create(
            title='React Fundamentals',
            description='Learn React',
            price=Decimal('79.99'),
            category=self.category
        )
        course2.instructor.add(self.instructor)

        Cart.objects.create(student=self.student, course=self.course)

        import time
        time.sleep(0.001)

        cart2 = Cart.objects.create(student=self.student, course=course2)

        cart_items = Cart.objects.filter(student=self.student).order_by('-added_at')
        self.assertEqual(cart_items.first(), cart2)



    def test_cannot_add_enrolled_course_to_cart(self):
        """Test that enrolled courses cannot be added to cart"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True
        )

        with self.assertRaises(ValidationError):
            cart_item = Cart(student=self.student, course=self.course)
            cart_item.save()

    def test_cart_item_removed_when_enrolled(self):
        """Test cart item is automatically removed when student enrolls"""
        Cart.objects.create(student=self.student, course=self.course)
        self.assertTrue(Cart.objects.filter(student=self.student, course=self.course).exists())

        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True
        )

        # Cart item should be automatically removed
        self.assertFalse(Cart.objects.filter(student=self.student, course=self.course).exists())
