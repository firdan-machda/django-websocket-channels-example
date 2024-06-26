import json
import random
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from faker import Faker
from faker.providers import lorem
from webpush import send_user_notification
from chat.models import ChatSession, ChatMessage, ChatUser

from asgiref.sync import sync_to_async
from rich import print as rprint


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        rprint(self.scope["user"])
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
            rprint(text_data)
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

        # simulate delay
        await asyncio.sleep(random.randint(0, 3))

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
        rprint("test...")
        # check chatsession exist
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "livechat_%s" % self.room_name
        try:
            rprint("Awaiting chat session and user...")
            self.chat_session = await ChatSession.objects.aget(session_uuid=self.room_name)
            rprint(f"connecting {self.scope['user']} with {self.chat_session}")
            user = self.scope["user"]
            await ChatUser.objects.aget(user__id=user.id, chat_session=self.chat_session)
        except (ChatUser.DoesNotExist, ChatSession.DoesNotExist):
            rprint("Chat session or user does not exist")
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        async for message in ChatMessage.objects.filter(chat_session__session_uuid=self.room_name).order_by("created_at").values("user__username", "message"):
            username = message["user__username"]
            msg = message["message"]
            owner = "Unknown" if username is None else username
            await self.send(text_data=json.dumps({"type": "message", "message": msg, "owner": owner}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        message = ""
        owner = self.scope["user"]
        if not owner.is_authenticated:
            return
        text_data_json = None
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            await ChatMessage.objects.acreate(chat_session=self.chat_session, user=owner, message=message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "text": json.dumps({
                        "type": "message",
                        "message": message,
                        "owner": owner.username
                    }
                    )
                }
            )
            # send notification to other users
            # async for chat_user in ChatUser.objects.filter(chat_session=self.chat_session).exclude(user=owner):
            #     usr = await sync_to_async(getattr)(chat_user, "user")
            #     payload = {
            #         'head': "New message {}".format(str(self.chat_session.session_uuid)),
            #         'body': "{}: {}".format(owner.username, message)
            #     }
            #     if usr != owner:
            #         await sync_to_async(send_user_notification)(user=usr, payload=payload)

    async def chat_message(self, event):
        await self.send(text_data=event["text"])
