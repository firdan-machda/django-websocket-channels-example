"""
ASGI config for channel project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'channel.settings')
django_asgi_app = get_asgi_application()

from .middleware import QueryAuthMiddleware
from chat.routing import websocket_urlpatterns as chat_routing
from webrtc.routing import websocket_urlpatterns as webrtc_routing
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)
    'websocket': QueryAuthMiddleware(
        URLRouter(
            chat_routing + webrtc_routing
        )
    ),
})

