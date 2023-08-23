# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from chat.routing import websocket_urlpatterns as chat_routing
from graph.schema import MyGraphqlWsConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat_routing
        )
    ),
    # 'websocket': URLRouter([
    #     path("graphql", MyGraphqlWsConsumer.as_asgi())
    # ])

})