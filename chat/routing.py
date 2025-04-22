from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<connect_announcement_id>\w+)/(?P<master_id>\w+)/(?P<client_id>\w+)/$", 
        consumers.ChatConsumer.as_asgi()
    ),
] 