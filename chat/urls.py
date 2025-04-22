from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.chat import ChatViewSet, ChatView

router = DefaultRouter()
router.register('', ChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Template view for chat UI
    path('room/<str:connect_announcement_id>/<str:master_id>/<str:client_id>/', 
         ChatView.as_view(), 
         name='chat_room'),
]
