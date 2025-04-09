from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from .swaggers import schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("captcha/", include("captcha.urls")),  # Captcha uchun URL-lar
    # accounts
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("dj_rest_auth.urls")),
    path("accounts/", include("dj_rest_auth.registration.urls")),
    # APPS
    path("announcements/", include("announcements.urls")),
    path("connect_announcements/", include("connect_announcements.urls")),
    path("images/", include("images.urls")),
    path("chat/", include("chat.urls")),
    path("industry/", include("industry.urls")),
    # hitcount
    path("hitcount/", include("hitcount.urls", namespace="hitcount")),
    # API authentication
    path("api/v1/drf-auth/", include("rest_framework.urls")),
    # API documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # JWT authentication
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", jwt_views.TokenVerifyView.as_view(), name="token_verify"),
    path(
        "api/token/blacklist/",
        jwt_views.TokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
]

# Static and media files for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
