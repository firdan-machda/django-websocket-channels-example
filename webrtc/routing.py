from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/video-call/(?P<room_name>(\w|\-)+)/$", consumers.WebRTCSignallingChannel.as_asgi()),
]