import graphene
from django.conf import settings
from .chatroom.query import Query as ChatroomQuery
from .webrtc.query import Query as WebRTCQuery
from .signaling.query import Query as SignalingQuery


class Query(WebRTCQuery, ChatroomQuery, SignalingQuery, graphene.ObjectType):
    """Root GraphQL query."""
    # Graphene requires at least one field to be present. Check
    # Graphene docs to see how to define queries.
    vapid_public_key = graphene.Field(graphene.String)

    def resolve_vapid_public_key(self, info):
        if info.context.user.is_authenticated:
            return settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
        return ""
