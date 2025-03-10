from django.urls import path, include
from .api.views import AnnouncementViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'announcement', AnnouncementViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
]
