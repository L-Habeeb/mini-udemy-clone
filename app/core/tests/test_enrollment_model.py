"""
Test for Enrollment Model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from core.models import Course, Category, SubCategory, Enrollment

User = get_user_model()


class EnrollmentModelTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            email='student@test.com',
            password='Testpass123!'
        )
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='Testpass123!',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='web development'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            category=self.category,
            price=99.99
        )
        self.course.instructor.add(self.instructor)
        self.course.subcategory.add(self.subcategory)

    def test_enrollment_creation(self):
        """Test basic enrollment creation"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_active)

    def test_enrollment_string_representation(self):
        """Test enrollment string representation"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        expected_str = f"{self.student.email} enrolled in {self.course.title}"
        self.assertEqual(str(enrollment), expected_str)

    def test_unique_constraint_prevents_duplicate_enrollment(self):
        """Test that same user cannot enroll in same course twice"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )

    def test_instructor_can_enroll_in_courses(self):
        """Test that instructors can enroll as students"""
        enrollment = Enrollment.objects.create(
            student=self.instructor,
            course=self.course
        )

        self.assertEqual(enrollment.student, self.instructor)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_active)

    def test_student_can_enroll_in_multiple_courses(self):
        """Test that one student can enroll in multiple courses"""
        course2 = Course.objects.create(
            title='Django Basics',
            description='Learn Django',
            category=self.category,
            price=149.99
        )
        course2.instructor.add(self.instructor)
        course2.subcategory.add(self.subcategory)

        enrollment1 = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        enrollment2 = Enrollment.objects.create(
            student=self.student,
            course=course2
        )

        self.assertEqual(self.student.enrollments.count(), 2)
        self.assertIn(enrollment1, self.student.enrollments.all())
        self.assertIn(enrollment2, self.student.enrollments.all())

    def test_course_can_have_multiple_enrollments(self):
        """Test that one course can have multiple students"""
        student2 = User.objects.create_user(
            email='student2@test.com',
            password='Testpass123!'
        )

        enrollment1 = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        enrollment2 = Enrollment.objects.create(
            student=student2,
            course=self.course
        )

        self.assertEqual(self.course.enrollments.count(), 2)
        self.assertIn(enrollment1, self.course.enrollments.all())
        self.assertIn(enrollment2, self.course.enrollments.all())

    def test_enrollment_ordering_by_enrolled_at_desc(self):
        """Test enrollments are ordered by enrolled_at descending"""
        student2 = User.objects.create_user(
            email='student2@test.com',
            password='Testpass123!'
        )

        enrollment1 = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        enrollment2 = Enrollment.objects.create(
            student=student2,
            course=self.course
        )

        enrollments = list(Enrollment.objects.all())
        self.assertEqual(enrollments[0], enrollment2)
        self.assertEqual(enrollments[1], enrollment1)

    def test_related_manager_access(self):
        """Test reverse relationship access via related managers"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        self.assertIn(enrollment, self.student.enrollments.all())

        self.assertIn(enrollment, self.course.enrollments.all())
