import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.db import try_get_member_from_user_room
from chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user = self.scope["user"]
        self.room_group_name = f"chat_{self.room_id}"

        if not self.user.is_authenticated:
            return await self.close()

        member = await try_get_member_from_user_room(self.user, self.room_id)
        if not member:
            return await self.close()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        member = await try_get_member_from_user_room(self.user, self.room_id)
        if member:
            await save_message(member, message)

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )


@database_sync_to_async
def save_message(member, content):
    return Message.objects.create(member=member, content=content)
