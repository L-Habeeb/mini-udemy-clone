"""
User Serializer
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for the User object"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'name',]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }


    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def validate_password(self, value):
        """
        Custom password validation with
         checking at least one Uppercase, lowecase and char
         """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[@#$%^&*!]", value):
            raise serializers.ValidationError("Password must contain at least one special character "
                                              "(@, #, $, %, ^, &, *, !).")

        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'name', 'bio']
        read_only = 'id'


class InstructorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Instructor Profile"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'role', 'bio']
        read_only_fields = ['id', 'email']
