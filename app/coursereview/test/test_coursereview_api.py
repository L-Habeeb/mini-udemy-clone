"""
Test for CourseReview API
"""
from rest_framework.test import APITestCase
from django.urls import reverse
from core.models import User, Course, Category, SubCategory, Enrollment, CourseReview


class CourseReviewAPITests(APITestCase):
    def setUp(self):
        """Set up test data for API tests"""
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            role='instructor'
        )
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            role='student'
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

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_unauthenticated_create_review_denied(self):
        """Test that unauthenticated users cannot create reviews"""
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {
            'rating': 5,
            'review_text': 'Great course!'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_non_enrolled_student_create_review_denied(self):
        """Test that non-enrolled students cannot create reviews"""
        self.client.force_authenticate(user=self.student2)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {
            'rating': 5,
            'review_text': 'Great course!'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_enrolled_student_create_review_success(self):
        """Test that enrolled student can create review"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {
            'rating': 5,
            'review_text': 'Excellent course! Highly recommended.'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        review = CourseReview.objects.get(student=self.student, course=self.course)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, 'Excellent course! Highly recommended.')

        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['review_text'], 'Excellent course! Highly recommended.')

    def test_create_review_rating_only(self):
        """Test creating review with only rating (no text)"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {'rating': 4}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['review_text'], '')

    def test_create_duplicate_review_denied(self):
        """Test that duplicate reviews are prevented at API level"""
        # Create first review
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='First review'
        )

        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {
            'rating': 3,
            'review_text': 'Duplicate review'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('already reviewed', str(response.data).lower())

    def test_list_course_reviews(self):
        """Test listing all reviews for a course"""
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Excellent!'
        )

        Enrollment.objects.create(student=self.student2, course=self.course)
        CourseReview.objects.create(
            student=self.student2,
            course=self.course,
            rating=4,
            review_text='Good course'
        )

        url = reverse('course:course-review-list', kwargs={'course_id': self.course.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        # Verify ordering (most recent first)
        self.assertEqual(response.data['results'][0]['rating'], 4)
        self.assertEqual(response.data['results'][1]['rating'], 5)

    def test_update_own_review_success(self):
        """Test that student can update their own review"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=3,
            review_text='Original review'
        )

        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-update', kwargs={
            'course_id': self.course.id,
            'course_review_id': review.id
        })
        data = {
            'rating': 5,
            'review_text': 'Updated review - much better!'
        }

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)

        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, 'Updated review - much better!')

    def test_update_others_review_denied(self):
        """Test that student cannot update another student's review"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Great course'
        )

        # Try to update as student2
        self.client.force_authenticate(user=self.student2)
        url = reverse('course:course-review-update', kwargs={
            'course_id': self.course.id,
            'course_review_id': review.id
        })
        data = {
            'rating': 1,
            'review_text': 'Terrible course'
        }

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)

        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, 'Great course')

    def test_update_nonexistent_review_not_found(self):
        """Test updating non-existent review returns 404"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-update', kwargs={
            'course_id': self.course.id,
            'course_review_id': 888  # Non-existent
        })
        data = {'rating': 5}

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 404)

    def test_invalid_rating_validation(self):
        """Test API validates rating range (already tested in model, but API should handle gracefully)"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})

        # Test invalid ratings
        for invalid_rating in [0, 6, -1]:
            with self.subTest(rating=invalid_rating):
                data = {'rating': invalid_rating}
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 400)
                self.assertIn('rating', str(response.data).lower())

    def test_missing_rating_validation(self):
        """Test that rating is required"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': self.course.id})
        data = {'review_text': 'Great course!'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', str(response.data).lower())

    def test_invalid_course_id_not_found(self):
        """Test creating review for non-existent course"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course:course-review-create', kwargs={'course_id': 999})
        data = {'rating': 5}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
