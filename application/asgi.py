"""
ASGI config for application project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.socketServer.urls import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 原有 HTTP 路由
    "websocket": AuthMiddlewareStack(  # WebSocket 路由
        URLRouter(websocket_urlpatterns)
    ),
})
