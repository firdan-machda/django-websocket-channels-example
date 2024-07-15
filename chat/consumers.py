from channels.generic.websocket import AsyncWebsocketConsumer
import json
import random
from faker import Faker
from faker.providers import lorem
import asyncio
from webpush import send_user_notification
from chat.models import ChatSession, ChatMessage, ChatUser

from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope["user"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        await self.chat_message({"type": "chat_message",
                                 "message": "welcome to channels demo",
                                 "owner": "server"})
        await self.chat_message({"type": "chat_message",
                                 "message": "available command is coinflip, lorem, ping and random",
                                 "owner": "server"})

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        message = ""
        owner = ""
        answer = ""
        text_data_json = None

        if text_data:
            print(text_data)
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            owner = text_data_json["owner"]
            answer = text_data_json.get("answer")

        await self.system_message({"type": "system_message", "signal": "loading"})

        # Send message to room group
        if message and not answer:
            await self.chat_message(
                {"type": "chat_message", "message": message, "owner": owner})
        elif answer:
            await self.chat_message(
                {"type": "chat_message", "message": answer, "owner": owner})

        await asyncio.sleep(3)
        # TODO: restructure this
        if message == "random":
            response = "Here's a random number ranging between 0-99: {}\n".format(
                random.randint(0, 99)
            )
            await self.chat_message(
                {"type": "chat_message", "message": response, "owner": "server"}
            )
        elif message == "ping":
            await self.chat_message(
                {"type": "chat_message", "message": "pong", "owner": "server"}
            )
        elif message == "lorem":
            fake = Faker()
            fake.add_provider(lorem)
            await self.chat_message(
                {"type": "chat_message",
                 "message": fake.paragraph(nb_sentences=10),
                 "owner": "server"}
            )
        elif message == "coinflip":
            if answer:
                result = "heads" if bool(random.getrandbits(1)) else "tails"

                await self.chat_message({"message": "Flipped {}".format(result), "owner": "server"})
                if result == answer:
                    await self.chat_message({"message": "Your guess is correct!", "owner": "server"})
                else:
                    await self.chat_message({"message": "Your guess is incorrect!", "owner": "server"})
            else:
                await self.chat_message({"message": "Guess coinflip: heads or tails?", "owner": "server"})
                await self.prompt_action({"choices": [{"name": "Heads", "alias": "heads"}, {"name": "Tails", "alias": "tails"}]})
        else:
            # invalid command
            response = "Sorry, I don't recognise the command. Available command is random, lorem and ping"
            await self.chat_message(
                {"type": "chat_message", "message": response, "owner": "server"}
            )
        await self.system_message(
            {"type": "system_message", "signal": "finished-loading"})

    # Receive message from room group

    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        print(self.scope["user"])
        await self.send(text_data=json.dumps({"type": "message", "message": message, "owner": event['owner']}))

    async def system_message(self, event):
        message = event["signal"]
        await self.send(text_data=json.dumps({"type": "system", "message": message}))

    async def prompt_action(self, event):
        choices = event["choices"]
        await self.send(text_data=json.dumps({"type": "action", "choices": choices, "owner": "server"}))


class LiveChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        def _find_count(chat_session):
            return ChatUser.objects.filter(chat_session=chat_session).count()
        # check chatsession exist
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "livechat_%s" % self.room_name
        try:
            self.chat_session = await ChatSession.objects.aget(session_uuid=self.room_name)
            # await ChatUser.objects.aget(user=self.scope["user"], chat_session=self.chat_session)
        except (ChatSession.DoesNotExist):
            await self.close()
            return

        await ChatUser.objects.aget_or_create(chat_session=self.chat_session, user=self.scope["user"])

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        if (await sync_to_async(_find_count)(self.chat_session)) >= 2:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.handshake",
                    "text": json.dumps({
                        "type": "init-handshake",
                        "owner": "server"
                    })
                }
            )

    async def disconnect(self, close_code):
        def _delete_chat_user(chat_session, user):
            ChatUser.objects.filter(
                chat_session=chat_session, user=user).delete()
        sync_to_async(_delete_chat_user)(
            self.chat_session, user=self.scope["user"])
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def notify_user(self, message):
        owner = self.scope["user"]
        async for chat_user in ChatUser.objects.filter(chat_session=self.chat_session).exclude(user=owner):
            usr = await sync_to_async(getattr)(chat_user, "user")
            payload = {
                'head': "New message {}".format(
                    str(self.chat_session.session_uuid)),
                'body': "{}: {}".format(
                    owner.username, message)
            }
            if usr != owner:
                await sync_to_async(send_user_notification)(
                    user=usr, payload=payload)

    async def receive(self, text_data):
        message = ""
        owner = self.scope["user"]
        if not owner.is_authenticated:
            return
        text_data_json = None
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            message_type = text_data_json.get("type", "")
            if message_type == "handshake":
                print(text_data_json)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.handshake",
                        "text": json.dumps({
                            "type": "handshake",
                            "message": message,
                            "owner": owner.username
                        }),
                    }
                )
                return
            # await ChatMessage.objects.acreate(chat_session=self.chat_session,user=owner,message=message)
            iv = text_data_json["iv"]
            algorithm = text_data_json["algorithm"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "text": json.dumps({
                        "type": "message",
                        "message": message,
                        "owner": owner.username,
                        "iv": iv,
                        "algorithm": algorithm,
                    }),
                }
            )
            self.notify_user(message)

    async def chat_message(self, event):
        await self.send(text_data=event["text"])

    async def chat_handshake(self, event):
        user = self.scope["user"]
        owner = json.loads(event["text"])["owner"]
        if user.username != owner:
            await self.send(text_data=event["text"])
