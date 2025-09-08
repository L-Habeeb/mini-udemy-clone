"""
URL configuration for app project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView,
                                   SpectacularSwaggerView,
                                   SpectacularRedocView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    # path('api/courses/', include('courses.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
