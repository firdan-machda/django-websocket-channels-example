from channels.generic.websocket import AsyncWebsocketConsumer
import json
import random
from faker import Faker
from faker.providers import lorem
import asyncio


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
                                 "message": "available command is random, lorem and ping",
                                 "owner": "server"})

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        message = ""
        owner = ""
        text_data_json = None

        if text_data:
            print(text_data)
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            owner = text_data_json["owner"]
            # Send message to room group

        await self.system_message({"type": "system_message", "signal": "loading"})

        if message:
            await self.chat_message(
                {"type": "chat_message", "message": message, "owner": owner})
        valid = False
        if message == "random":
            valid = True
            response = "Here's a random number ranging between 0-99: {}\n".format(
                random.randint(0, 99)
            )
            await self.chat_message(
                {"type": "chat_message", "message": response, "owner": "server"}
            )

        if message == "ping":
            valid = True
            await self.chat_message(
                {"type": "chat_message", "message": "pong", "owner": "server"}
            )

        if message == "lorem":
            valid = True
            fake = Faker()
            fake.add_provider(lorem)

            await asyncio.sleep(3)
            await self.chat_message(
                {"type": "chat_message",
                 "message": fake.paragraph(),
                 "owner": "server"}
            )
        await self.system_message(
            {"type": "system_message", "signal": "finished-loading"})
        if not valid:
            # invalid command
            response = "Sorry, I don't recognise the command. Available command is random, lorem and ping"
            await self.chat_message(
                {"type": "chat_message", "message": response, "owner": "server"}
            )

    # Receive message from room group

    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        print(self.scope["user"])
        await self.send(text_data=json.dumps({"type": "message", "message": message, "owner": event['owner']}))

    async def system_message(self, event):
        message = event["signal"]
        await self.send(text_data=json.dumps({"type": "system", "message": message}))
