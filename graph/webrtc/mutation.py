import graphene
from graphql.error import GraphQLError
from webrtc.models import WebRTCSession, WebRTCUser


class JoinVideoChatroomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String()

    chatroom_id = graphene.String()

    def mutate(self, info, chatroom_id=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("user is not logged in")
        if chatroom_id is None:
            # create new chatroom
            new_chatsession = WebRTCSession.objects.create()
            WebRTCUser.objects.get_or_create(
                webrtc_session=new_chatsession, user=user)
            return JoinVideoChatroomMutation(chatroom_id=new_chatsession.session_uuid)
        try:
            chatsession = WebRTCSession.objects.get(session_uuid=chatroom_id)
            if WebRTCUser.objects.filter(webrtc_session=chatsession).count() >= 2:
                raise GraphQLError("room is full")

            WebRTCUser.objects.get_or_create(
                webrtc_session=chatsession, user=user)
            return JoinVideoChatroomMutation(chatroom_id=str(chatsession.session_uuid))
        except WebRTCSession.DoesNotExist:
            raise GraphQLError("chat session does not exist")


class LeaveVideoChatroomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String(required=True)

    status = graphene.Int()

    def mutate(self, info, chatroom_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("user is not logged in")
        WebRTCUser.objects.filter(
            webrtc_session__pk=chatroom_id, user=user).delete()
        return LeaveVideoChatroomMutation(status=201)


class Mutation(graphene.ObjectType):
    join_video_chatroom = JoinVideoChatroomMutation.Field()
    leave_video_chatroom = LeaveVideoChatroomMutation.Field()
