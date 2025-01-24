import graphene
from django.conf import settings
from webrtc.models import WebRTCUser


class Query(graphene.ObjectType):
    video_chatrooms = graphene.Field(graphene.List(graphene.String))

    def resolve_chatrooms(self, info):
        user = info.context.user
        if user.is_authenticated:
            return (list(WebRTCUser.objects.filter(user=user).values_list("webrtc_session__session_uuid", flat=True)))
        return []
