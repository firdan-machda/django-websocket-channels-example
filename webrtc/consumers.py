import json

from django.db.models import Q
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from webrtc.models import WebRTCSession, WebRTCUser

class WebRTCSignallingChannel(AsyncWebsocketConsumer):
    async def connect(self):
        def _find_count(chat_session):
            return WebRTCUser.objects.filter(webrtc_session=chat_session).count()
        # check chatsession exist
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "webrtc_%s" % self.room_name
        try:
            self.chat_session = await WebRTCSession.objects.aget(Q(session_uuid=self.room_name)|Q(alias=self.room_name))
            # await ChatUser.objects.aget(user=self.scope["user"], chat_session=self.chat_session)
        except (WebRTCSession.DoesNotExist):
            await self.close()
            return

        if (await sync_to_async(_find_count)(self.chat_session)) > 2:
            await self.close(code=400)
            return

        await WebRTCUser.objects.aget_or_create(webrtc_session=self.chat_session, user=self.scope["user"])

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user.message", "text": json.dumps({"type": "user-join", "owner": self.scope["user"].username})
            }
        )
        if (await sync_to_async(_find_count)(self.chat_session)) >= 2:
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
        print(text_data_json)
        if text_data_json["type"] == "offer":
            data = text_data_json.get("data", {"type": "offer"})
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-offer", "owner": self.scope["user"].username, "data": data})
                }
            )
        elif text_data_json["type"] == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-candidate", "owner": self.scope["user"].username, "data": text_data_json["data"]})
                }
            )
        else:
            return await super().receive(text_data)

    async def user_message(self, event):
        user = self.scope["user"]
        owner = json.loads(event["text"])["owner"]
        if user.username != owner:
            await self.send(text_data=event["text"])

    async def chat_handshake(self, event):
        await self.send(text_data=event["text"])

    async def disconnect(self, close_code):
        print(self.scope["user"], "disconnecting")
        message = "disconnected"

        if close_code == 400:
            message = "room is full"

        def _delete_chat_user(chat_session, user):
            deleted = WebRTCUser.objects.filter(
                webrtc_session=chat_session, user=user).delete()
            print("Deleted ", deleted)

        await sync_to_async(_delete_chat_user)(
            self.chat_session, user=self.scope["user"])
        
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user.message",
                "text": json.dumps({"type": "user-disconnect", "owner": self.scope["user"].username, message: message})
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
