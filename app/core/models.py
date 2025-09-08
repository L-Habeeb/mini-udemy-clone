"""
API Models
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
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


class Section(models.Model):
    """Section Model"""
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course,
        related_name='sections',
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField()

    @property
    def lecture_count(self):
        return self.lectures.count()

    @property
    def total_duration(self):
        return self.lectures.aggregate(
            total=models.Sum('duration')
        )['total'] or 0

    def get_duration_display(self):
        """Format duration as '1h 37min' or '37min'"""
        total_seconds = self.total_duration
        if total_seconds == 0:
            return '0min'

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f'{hours}h {minutes}min'
        return f'{minutes}min'

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        """Ensure validation runs on save"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Lecture(models.Model):
    """Lecture Model"""

    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('article', 'Article'),
        ('file', 'File'),
    ]

    title = models.CharField(max_length=255)
    section = models.ForeignKey(
        Section,
        related_name='lectures',
        on_delete=models.CASCADE,
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES
    )
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    order = models.PositiveIntegerField()
    is_preview = models.BooleanField(default=False)

    video = models.FileField(upload_to='lectures/videos/', blank=True, null=True)
    article = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="lectures/files/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Custom validation for business rules"""
        super().clean()

        # Validation Rule 1: Videos must have duration > 0
        if self.content_type == 'video' and self.duration <= 0:
            raise ValidationError({
                'duration': 'Video lectures must have a duration greater than 0 seconds.'
            })

        # Validation Rule 2: Only one content field should be provided
        content_fields = [
            (self.video, 'video'),
            (self.article, 'article'),
            (self.file, 'file')
        ]

        provided_fields = [name for field, name in content_fields if field]

        if len(provided_fields) == 0:
            raise ValidationError({
                'content': 'You must provide either a video, article, or file for the lecture.'
            })

        if len(provided_fields) > 1:
            raise ValidationError({
                'content': f'You cannot provide multiple content types. Found: {", ".join(provided_fields)}'
            })

        # Validation Rule 3: Content must match content_type
        if self.content_type == 'video' and not self.video:
            raise ValidationError({
                'video': 'Video content is required for video lectures.'
            })

        if self.content_type == 'article' and not self.article:
            raise ValidationError({
                'article': 'Article content is required for article lectures.'
            })

        if self.content_type == 'file' and not self.file:
            raise ValidationError({
                'file': 'File is required for file lectures.'
            })

    def get_duration_display(self):
        """Format duration as '5:20' or '1:23:45'"""
        if self.duration == 0:
            return '0:00'

        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60

        if hours > 0:
            return f'{hours}:{minutes:02d}:{seconds:02d}'
        return f'{minutes}:{seconds:02d}'

    def save(self, *args, **kwargs):
        """Ensure validation runs on save"""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

