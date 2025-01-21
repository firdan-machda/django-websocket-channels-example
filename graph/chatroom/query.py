import graphene
from django.conf import settings
from chat.models import ChatUser
from django.db.models import TextField
from django.db.models.functions import Cast


class Query(graphene.ObjectType):
    chatrooms = graphene.Field(graphene.List(graphene.String))
    def resolve_chatrooms(self, info):
        user = info.context.user
        if user.is_authenticated:
            return (list(ChatUser.objects.filter(user=user).values_list("chat_session__session_uuid", flat=True)))
        return []
