import graphene
import uuid

from django.db.models import Q
from graphql.error import GraphQLError
from signaling.models import WebRTCSession, WebRTCUser, WebRTCOffer


def is_valid_uuid(uuid_to_test, version=4):
    try:
        # check for validity of Uuid
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True


class CreateVideoRoomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String()
        username = graphene.String(required=True)

    chatroom_id = graphene.String()
    alias = graphene.String()

    def mutate(self, info, chatroom_id=None, username=None):
        if username is not None:
            WebRTCUser.objects.get_or_create(username=username)

        if chatroom_id is None:
            # create new chatroom
            new_chatsession = WebRTCSession.objects.create()

            return CreateVideoRoomMutation(chatroom_id=str(new_chatsession.session_uuid))

        try:
            # check valid uuid
            if not is_valid_uuid(chatroom_id):
                chatsession, created = WebRTCSession.objects.get_or_create(alias=chatroom_id)
            else:
                chatsession = WebRTCSession.objects.get(
                    session_uuid=chatroom_id)

            return CreateVideoRoomMutation(chatroom_id=str(chatsession.session_uuid), alias=str(chatsession.alias))
        except WebRTCSession.DoesNotExist:
            raise GraphQLError("video session does not exist")


class LeaveVideoRoomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String(required=True)
        username = graphene.String(required=True)

    status = graphene.Int()

    def mutate(self, info, chatroom_id, username):
        # remove offer from the database
        WebRTCOffer.objects.filter(
            webrtc_session__pk=chatroom_id, user__username=username).delete()

        return LeaveVideoRoomMutation(status=201)


class Mutation(graphene.ObjectType):
    create_video_room = CreateVideoRoomMutation.Field()
    leave_video_room = LeaveVideoRoomMutation.Field()
