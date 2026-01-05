# Development specific settings
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - Use your actual database name
DATABASES['default']['NAME'] = 'i2'  # Remove this line if you want to use .env only
ADMIN_REGISTRATION_CODE = os.environ.get('ADMIN_REGISTRATION_CODE', 'DEFAULT_SECURE_CODE')

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Less strict security for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging more verbose in development
LOGGING['root']['level'] = 'DEBUG'

# ============================================================================
# ADDITIONAL NOTES FOR TESTING WITHOUT AUTHENTICATION:
# ============================================================================
# If you want to test API endpoints without authentication, you can modify 
# REST_FRAMEWORK settings in this file:

# Option 1: Allow all requests without authentication
# REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
#     'rest_framework.permissions.AllowAny',
# ]

# Option 2: Keep read-only for GET, allow all for others
# REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
#     'rest_framework.permissions.IsAuthenticatedOrReadOnly',
# ]
# In your settings.py or wherever you configure drf-yasg
SWAGGER_SETTINGS = {
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'DEFAULT_INFO': 'your_project.urls.schema_view',  # Adjust this
}

# Or exclude specific endpoints
def should_include_endpoint(endpoint):
    if 'accounts' in endpoint[0] and 'profile' in endpoint[0]:
        return False
    return True