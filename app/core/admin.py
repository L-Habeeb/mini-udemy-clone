"""
Customizing our Admin Site
"""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'role', 'bio','is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('role', 'bio')}),
        (
            _('Permissions'), {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'role',
                'bio',
                'is_active',
                'is_staff',
                'is_superuser'
            ),
        }),
    )
    search_fields = ['email', 'role']

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Course)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Section)
admin.site.register(models.Lecture)
