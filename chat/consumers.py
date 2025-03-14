import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from chat.models import Member


class ChatConsumer(AsyncWebsocketConsumer):
    user: User
    room_name: str

    async def connect(self):
        print("Connecting")

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            print("user not authenticated")
            return await self.close()

        print('user: ', self.user)

        member = await try_get_member_from_user_room(self.user, self.room_name)

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
def get_user(user_id: int):
    user = User.objects.get(pk=user_id)

    return user


@database_sync_to_async
def try_get_member_from_user_room(user: User, room_name: str):
    try:
        return Member.objects.get(user=user, room__name=room_name)
    except Member.DoesNotExist:
        return None


@database_sync_to_async
def get_name():
    return User.objects.all()[0].name
