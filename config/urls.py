"""
URL configuration for volunteer_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# API Documentation imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Optional: If you want to use DRF's built-in docs
try:
    from rest_framework.documentation import include_docs_urls
    DRF_DOCS_AVAILABLE = True
except ImportError:
    DRF_DOCS_AVAILABLE = False

# Health check endpoint
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for API monitoring"""
    return Response({
        "status": "ok",
        "message": "Volunteer Platform API is running",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "accounts": "/api/accounts/",
            "skills": "/api/skills/",
            "missions": "/api/missions/",
            "communications": "/api/communications/",
            "audit": "/api/audit/",
            "admin": "/admin/",
            "api_docs": "/swagger/",
            "api_docs_alt": "/redoc/"
        }
    })

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Volunteer Platform API",
        default_version='v1.0',
        description="""
        # Volunteer Management Platform API
        
        ## User Roles & Permissions:
        - **Admin**: Full system access (manage skills, categories, verify skills)
        - **Volunteer**: Manage own skills, request verification
        - **Organization**: Create missions, manage mission skills, search volunteers
        - **Public**: Read-only access to skills and categories
        
        ## Authentication:
        - Use JWT tokens: `Authorization: Bearer <your_token>`
        - Get token: `POST /api/accounts/login/`
        
        ## Quick Links:
        - [Skills Module](/api/skills/)
        - [Accounts Module](/api/accounts/)
        - [Missions Module](/api/missions/)
        
        ## Testing Mode:
        During development, permissions are set to `AllowAny` for testing.
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API Health Check
    path('api/health/', health_check, name='health-check'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), 
         name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    # Optional: DRF built-in docs (if coreapi is installed)
    *([path('api/docs/', include_docs_urls(
        title='API Documentation',
        permission_classes=[AllowAny]
    ))] if DRF_DOCS_AVAILABLE else []),
    
    # Application URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/missions/', include('apps.missions.urls')),
    path('api/skills/', include('apps.skills.urls')),
    path('api/communications/', include('apps.communications.urls')),
    path('api/audit/', include('apps.audit.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar (if installed)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass