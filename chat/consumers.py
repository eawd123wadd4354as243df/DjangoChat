import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    user: User


    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            print("user not authenticated")
            return

        print('user: ', self.user)
        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


@database_sync_to_async
def get_user(user_id: int):
    user = User.objects.get(pk=user_id)

    return user


@database_sync_to_async
def get_name():
    return User.objects.all()[0].name
