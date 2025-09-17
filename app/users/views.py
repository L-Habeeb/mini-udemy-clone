"""
User Views
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView

from users import serializers

user = get_user_model()

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            )
        ]
    )
)

class UserRegistrationView(generics.CreateAPIView):
    """Views for User registration and Token returned"""
    queryset = user.objects.all()
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Create user and return token in response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        response_data = serializer.data.copy()
        response_data.pop('password', None)
        response_data['token'] = token.key

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Views for User Profile Detail, update, delete"""
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserProfileSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class BecomeInstructorView(APIView):
    """Allow aunthenticated user to become Instructor"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=serializers.InstructorProfileSerializer,
        responses={200: serializers.InstructorProfileSerializer},
        description="Upgrade user role to instructor. Optional: update bio."
    )

    def post(self, request):
        current_user = self.request.user

        if current_user.role == 'instructor':
            return Response(
                {'error': 'You are already an instructor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        current_user.role = 'instructor'
        bio = request.data.get('bio')
        current_user.bio = bio
        current_user.save()
        serializer = serializers.InstructorProfileSerializer(current_user)
        return Response({
            'message': 'Successfully became an instructor!',
            'Instructor-Profile': serializer.data
        }, status=status.HTTP_200_OK)
