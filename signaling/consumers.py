import json

from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import WebRTCOffer, WebRTCUser, WebRTCSession


class WebRTCSignallingChannel(AsyncWebsocketConsumer):
    async def connect(self):
        # check chatsession exist
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "signaling_%s" % self.room_name
        try:
            self.chat_session = await WebRTCSession.objects.aget(Q(session_uuid=self.room_name) | Q(alias=self.room_name))
            # await ChatUser.objects.aget(user=self.scope["user"], chat_session=self.chat_session)
        except (WebRTCSession.DoesNotExist):
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.handshake",
                "text": json.dumps({
                    "type": "init-handshake",
                })
            }
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        username = text_data_json.get("username")
        current_user = WebRTCUser.objects.aget_or_create(username=username)
        self.current_username = current_user.username

        if text_data_json["type"] == "all-offer":
            data = text_data_json.get("data", {"type": "offer"})
            # list all available offer
            offers = WebRTCOffer.objects.afilter(webrtc_session=self.chat_session).exclude(
                user__username=current_user).values("offer", "user__username")
            serialize = json.dumps(list(offers), cls=DjangoJSONEncoder)

            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-all-offer", "data": serialize})
                }
            )
        elif text_data_json["type"] == "offer":
            # user send an offer, save it to the database then broadcast it to the other user
            await WebRTCOffer.objects.acreate(
                webrtc_session=self.chat_session, username=current_user, offer=text_data_json["data"])
            data = text_data_json.get("data", {"type": "offer"})
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-offer", "owner": current_user.username, "data": data})
                }
            )
        elif text_data_json["type"] == "candidate":
            # broadcast candidate to group
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-candidate", "owner": current_user.username, "data": text_data_json["data"]})
                }
            )
        else:
            return await super().receive(text_data)

    async def user_message(self, event):
        user = self.scope["user"]
        owner = json.loads(event["text"])["owner"]
        if user.username != owner:
            await self.send(text_data=event["text"])

    async def disconnect(self, close_code):
        message = "disconnected"

        def _delete_chat_user(chat_session, user):
            deleted = WebRTCOffer.objects.filter(
                webrtc_session=chat_session, user=user).delete()
            print("Deleted ", deleted)

        await sync_to_async(_delete_chat_user)(
            self.chat_session, user=self.current_username)

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user.message",
                "text": json.dumps({"type": "user-disconnect", "owner": self.current_username, "text": message})
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
