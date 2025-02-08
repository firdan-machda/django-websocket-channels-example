import json

from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import WebRTCOffer, WebRTCUser, WebRTCSession


class WebRTCSignallingChannel(AsyncWebsocketConsumer):
    current_username = None

    async def connect(self):
        # check chatsession exist
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "signaling_%s" % self.room_name
        try:
            self.chat_session = await WebRTCSession.objects.aget(Q(session_uuid=self.room_name) | Q(alias=self.room_name))
        except (WebRTCSession.DoesNotExist):
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        username = text_data_json.get("owner")

        # simple logic to check whether username is empty or not
        # username is required to identify the user to prevent self message
        if username:
            current_user, created = await WebRTCUser.objects.aget_or_create(username=username)
            self.current_username = current_user.username
            if created:
                print("Created new user: ", current_user)
        else:
            await self.send_error("username is empty")
            await self.close(code=4000)
            return

        print(text_data_json["type"] == "clear-session")
        if text_data_json["type"] == "clear-session":
            # clear all offer in this session
            self.close()
            return

        if text_data_json["type"] == "all-offer":
            data = text_data_json.get("data", {"type": "offer"})
            # list all available offer
            offers = await sync_to_async(lambda: WebRTCOffer.objects.filter(webrtc_session=self.chat_session).exclude(
                user__username=current_user).values("offer", "user__username"))()
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
                webrtc_session=self.chat_session, user=current_user, offer=text_data_json["data"])
            data = text_data_json.get("data", {"type": "offer"})
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-offer", "owner": current_user.username, "data": data})
                }
            )
        elif text_data_json["type"] == "answer": 
            data = text_data_json.get("data", {"type": "answer"})
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-answer", "owner": current_user.username, "data": data })
                }
            )
        elif text_data_json["type"] == "candidate":
            # save candidate to the database
            # await WebRTCOffer.objects.acreate(
            #     type="candidate", webrtc_session=self.chat_session,
            #     user=current_user, offer=text_data_json["data"])

            # def _get_available_candidates(user):
            #     offers = WebRTCOffer.objects.filter(
            #         type="candidate", webrtc_session=self.chat_session).exclude(user=user).values("offer", "user__username")
            #     offers_list = json.dumps(list(offers), cls=DjangoJSONEncoder)
            #     return offers_list
            
            # # offer all available candidate in this group
            # offers = await sync_to_async(_get_available_candidates)(user=current_user)
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user.message",
                    "text": json.dumps({"type": "user-candidate", "owner": current_user.username, "data": text_data_json["data"]})
                }
            )

        else:
            return await super().receive(text_data)

    async def send_error(self, message):
        await self.send(text_data=json.dumps({"type": "error", "message": message}))

    async def user_message(self, event):
        owner = json.loads(event["text"])["owner"]
        if self.current_username != owner:
            await self.send(text_data=event["text"])

    async def error_message(self, event):
        await self.send(text_data=event["text"])

    async def disconnect(self, close_code):
        print("Disconnected", close_code)

        def _delete_chat_user(chat_session, username):
            print("attempt delete %s"%username)
            deleted = WebRTCOffer.objects.filter(
                webrtc_session=chat_session, user__username=username).delete()

            print("Deleted %s"%username, deleted)

        await sync_to_async(_delete_chat_user)(
            self.chat_session, username=self.current_username)


        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
