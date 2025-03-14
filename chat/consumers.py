import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from chat.db import try_get_member_from_user_room


class ChatConsumer(AsyncWebsocketConsumer):
    user: User
    room_id: int

    async def connect(self):
        print("Connecting")

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            print("user not authenticated")
            return await self.close()

        print('user: ', self.user)

        member = await atry_get_member_from_user_room(self.user, self.room_id)

        if not member:
            print('member not found')
            return await self.close()

        print('member: ', member)

        print("Accepting connection")
        return await self.accept()


async def disconnect(self, close_code):
    print("Closing connection:", close_code)

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
def atry_get_member_from_user_room(user: User, room_id: id):
    return try_get_member_from_user_room(user, room_id)
