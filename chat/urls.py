from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name="chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("live/<str:room_name>/", TemplateView.as_view(template_name="room/livechat.html"), name="live"),
    path("computer/<str:room_name>/", views.room, name="room"),
]