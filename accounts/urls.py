from django.urls import path, include
from .views.websocket_test import index
from rest_framework.routers import DefaultRouter
from .api.views import UserViewSet, LogoutView, LoginView
from .api.masters import MasterAPIView

urlpatterns = [
    path("", index, name="index"),
]


router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns += [
    path("api/", include(router.urls)),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/masters/", MasterAPIView.as_view(), name="masters"),
    path("api/masters/<int:pk>/", MasterAPIView.as_view(), name="master"),
]
