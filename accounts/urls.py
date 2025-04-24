from django.urls import path, include
from .views.websocket_test import index
from rest_framework.routers import DefaultRouter
from .api.views import UserViewSet, LogoutView, LoginView
from .api.masters import MasterAPIView
from .views.custom_google_login import CustomGoogleLoginView

urlpatterns = [
    path("", index, name="index"),
]

router = DefaultRouter()
router.register(r'api/users', UserViewSet, basename='user')

urlpatterns += [
    path('', include(router.urls)),
    path('api/users/verify-email/', UserViewSet.as_view({'get': 'verify_email'}), name='verify-email'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/masters/", MasterAPIView.as_view(), name="masters"),
    path("api/masters/<int:pk>/", MasterAPIView.as_view(), name="master"),
    
    # Current user endpoint
    path('user/', UserViewSet.as_view({'get': 'current_user'}), name='current-user'),
    
    # Google login endpoints - providing multiple paths to ensure frontend can connect
    path("api/google-login/", CustomGoogleLoginView.as_view(), name="google-login"),
    path("api/google/login/", CustomGoogleLoginView.as_view(), name="google-login-alt"),
    path("accounts/api/google/login/", CustomGoogleLoginView.as_view(), name="google-login-accounts"),
    path("accounts/api/google-login/", CustomGoogleLoginView.as_view(), name="google-login-accounts-dash"),
]