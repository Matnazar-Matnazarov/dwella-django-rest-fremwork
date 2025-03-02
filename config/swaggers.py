from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings

# project name "Dwella building jobs"
# API documentation schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Dwella Building Jobs API",
        default_version='v1',
        description="""
        # Dwella Building Jobs REST API Documentation
        
        This API provides comprehensive endpoints for the Dwella Building Jobs platform.
        
        ## Key Features
        - User Authentication & Authorization
        - Job Management
        - Real-time Chat
        - File Upload/Download
        - Geolocation Services
        
        ## Authentication
        All authenticated endpoints require a valid JWT token in the Authorization header:
        `Authorization: Bearer <token>`
        
        ## Rate Limiting
        API requests are limited to 100 requests per minute per user.
        
        ## Support
        For technical support or API-related questions, please contact our support team.
        """,
        terms_of_service="https://www.dwella.com/terms/",
        contact=openapi.Contact(
            name="Dwella API Support",
            email="api@dwella.com",
            url="https://developers.dwella.com"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
        x_logo={
            "url": settings.STATIC_URL + "images/logo.png",
            "backgroundColor": "#FFFFFF",
            "altText": "Dwella logo"
        },
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
    patterns=None,  # Optional: specify URL patterns to include
    authentication_classes=[],  # Empty list to allow unauthenticated access to docs
    validators=['flex', 'ssv'],  # Enable additional validators
)
