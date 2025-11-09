"""auto_ski_info URL Configuration"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Auto Ski Info Subscribe API",
      default_version='v1',
      description="API for monitoring X (Twitter) accounts and processing with Gemini AI",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/monitor/', include('x_monitor.urls')),
    path('api/ai/', include('ai_service.urls')),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve React frontend for all non-API routes (SPA routing)
if settings.DEBUG or settings.FRONTEND_BUILD_DIR:
    urlpatterns += [
        re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html'), name='frontend'),
    ]