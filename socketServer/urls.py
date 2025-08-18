from django.urls import path
from .consumers.chat import ChatConsumer
from .consumers.notify import NotificationConsumer

websocket_urlpatterns = [
    path("ws/chat/<room_name>/", ChatConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
