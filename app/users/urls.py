from django.urls import path, include
from rest_framework.authtoken import views as drf_auth_views
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()
# router.register(r'profile', views.UserProfileView, basename='profile')

app_name = 'user'

urlpatterns = [
    # path('', include(router.urls)),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', drf_auth_views.obtain_auth_token, name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('become-instructor/', views.BecomeInstructorView.as_view(), name='become-instructor'),
]
