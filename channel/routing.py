# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from chat.routing import websocket_urlpatterns as chat_routing
from webrtc.routing import websocket_urlpatterns as webrtc_routing
from signaling.routing import websocket_urlpatterns as signaling_routing
from .middleware import QueryAuthMiddleware


routing_patterns  = [] + chat_routing + webrtc_routing + signaling_routing
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': QueryAuthMiddleware(
#         URLRouter(
#             chat_routing + webrtc_routing + signaling_routing
#         )
#     ),
# })