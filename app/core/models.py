"""
API Models
"""
from decimal import Decimal
from django.db.models import JSONField

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom User Manager for User Model Create_user and superuser"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email and password"""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password"""

        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('is_active') is not True:
            raise ValueError(_('Superuser must have is_active=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Our User Model extending default Django User Model"""
    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    bio = models.TextField(blank=True, max_length=500, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.email


class Category(models.Model):
    """Category Model"""
    name = models.CharField(
        max_length=125,
        unique=True,
    )
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """SubCategory Model"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategory',
    )
    name = models.CharField(
        max_length=125,
        unique=True,
    )
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'SubCategory'
        verbose_name_plural = 'SubCategories'

    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model with multiple instructors support"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    subcategory = models.ManyToManyField(
        SubCategory,
        related_name='courses',
    )
    objectives = JSONField(default=list)
    instructor = models.ManyToManyField(
        User,
        limit_choices_to={'role': 'instructor'},
        related_name='courses_taught',
        help_text="Instructors who teach this course"
    )
    LEVEL_CHOICES = [
        ("Beginner", "beginner"),
        ("Intermediate", "intermediate"),
        ("All-Level", "all-level"),
    ]

    title = models.CharField(max_length=125, null=False, blank=False, unique=True)
    description = models.TextField(null=False, blank=False)
    language = models.CharField(max_length=50, default="English")
    level = models.CharField(
        max_length=50,
        choices=LEVEL_CHOICES,
        default="all-levels"
    )
    requirements = models.TextField(max_length=100, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Course price in USD (0.00 for free courses)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_instructor_names(self):
        """Return comma-separated list of instructor names"""
        return ', '.join([instructor.name for instructor in self.instructor.all()])

    def __str__(self):
        return self.title

