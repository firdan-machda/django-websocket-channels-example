import graphene
from graphql.error import GraphQLError
from chat.models import ChatSession, ChatUser


class JoinChatroomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String()
    
    chatroom_id = graphene.String()
    
    def mutate(self, info, chatroom_id=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("user is not logged in") 
        if chatroom_id is None:
            # create new chatroom
            new_chatsession = ChatSession.objects.create()
            ChatUser.objects.get_or_create(chat_session=new_chatsession, user=user)
            return JoinChatroomMutation(chatroom_id=new_chatsession.session_uuid)
        try:
            chatsession = ChatSession.objects.get(session_uuid=chatroom_id)
            if ChatUser.objects.filter(chat_session=chatsession).count() >= 2:
                raise GraphQLError("room is full")

            ChatUser.objects.get_or_create(chat_session=chatsession, user=user)
            return JoinChatroomMutation(chatroom_id=str(chatsession.session_uuid))
        # register for notification?
        except ChatSession.DoesNotExist:
            raise GraphQLError("chat session does not exist")


class LeaveChatroomMutation(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.String(required=True)
    
    status = graphene.Int()

    def mutate(self, info, chatroom_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("user is not logged in")
        ChatUser.objects.filter(chat_session__pk=chatroom_id, user=user).delete()
        return LeaveChatroomMutation(status=201)


class Mutation(graphene.ObjectType):
    join_chatroom = JoinChatroomMutation.Field()
    leave_chatroom = LeaveChatroomMutation.Field()
