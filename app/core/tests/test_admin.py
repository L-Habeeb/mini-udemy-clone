from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class AdminSiteTests(TestCase):
    def setUp(self):
        """Set up test client and create a superuser"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_login(self.admin_user)  # Log in as admin
        self.user = User.objects.create_user(
            email='user@example.com',
            password='test123',
            role='student'
        )

    def test_users_listed(self):
        """Test that users are listed in admin"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.get_role_display())

    def test_user_change_page(self):
        """Test that user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
    
    def test_bio_field_in_user_admin(self):
        """Test that the bio field is displayed in the user admin"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertContains(res, 'bio')
        self.assertContains(res, self.user.bio or '')   
