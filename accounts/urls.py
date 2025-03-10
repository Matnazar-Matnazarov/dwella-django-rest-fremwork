from django.urls import path, include
from .views.websocket_test import index
from rest_framework.routers import DefaultRouter
from .api.views import UserViewSet, LogoutView, LoginView
from .api.masters_view import MastersView

urlpatterns = [
    path('', index, name='index'),
]


router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns += [
    path('api/', include(router.urls)),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/masters/', MastersView.as_view(), name='masters'),
]