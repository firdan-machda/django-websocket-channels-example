import graphene

from django.conf import settings
from signaling.models import WebRTCSession


class Query(graphene.ObjectType):
    video_rooms = graphene.Field(graphene.List(graphene.String))

    def resolve_video_rooms(self, info):
        return WebRTCSession.objects.values_list("session_uuid", flat=True)
