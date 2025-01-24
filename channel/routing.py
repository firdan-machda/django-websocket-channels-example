# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from chat.routing import websocket_urlpatterns as chat_routing
from webrtc.routing import websocket_urlpatterns as webrtc_routing
from .middleware import QueryAuthMiddleware

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': QueryAuthMiddleware(
        URLRouter(
            chat_routing + webrtc_routing
        )
    ),
})