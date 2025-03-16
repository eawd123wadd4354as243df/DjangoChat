from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User

from chat.db import try_get_member_from_user_room, add_user_to_room
from chat.models import Member, Message
from chat.payloads import FrontendChatSwitchPayload, FrontendMessagePayload, FrontendAddMemberPayload, GroupEvent, \
    GroupChatAddPayload, GroupChatSendPayload, BackendEvent


class ChatConsumer(AsyncJsonWebsocketConsumer):
    user: User = None
    room_id: int | None = None

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            return await self.close()

        await self.channel_layer.group_add(
            get_user_group_name(self.user.id),
            self.channel_name
        )

        return await self.accept()

    async def disconnect(self, close_code):
        print("Closing connection:", close_code)

        # Leave user group
        await self.channel_layer.group_discard(
            get_user_group_name(self.user.id),
            self.channel_name
        )

        # Leave room group
        if self.room_id is not None:
            await self.channel_layer.group_discard(
                get_room_group_name(self.room_id),
                self.channel_name
            )

    async def send_json(self, content: BackendEvent, close=False):
        await super().send_json(content, close)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        payload = content["payload"]

        # TODO except for chat.switch these should really be api calls
        match content["type"]:
            case "chat.switch":
                await self.switch_chat(payload)
            case "message.send":
                await self.receive_message(payload)
            case "member.add":
                await self.add_member(payload)

            case _:
                raise Exception("Unknown event type")

    async def switch_chat(self, payload: FrontendChatSwitchPayload):
        room_id = payload["chat_id"]

        member = await atry_get_member_from_user_room(self.user, room_id)

        if not member:
            print('member not found')
            return

        if self.room_id is not None:
            await self.channel_layer.group_discard(
                get_room_group_name(self.room_id),
                self.channel_name
            )

        await self.channel_layer.group_add(
            get_room_group_name(room_id),
            self.channel_name
        )
        self.room_id = room_id

    async def receive_message(self, payload: FrontendMessagePayload):
        message = payload['content']
        if message.isspace():
            return

        member = await atry_get_member_from_user_room(self.user, self.room_id)

        if member is None:
            raise Exception("User not in room")


        db_message = await asave_message(member, message)
        await self.channel_layer.group_send(
            get_room_group_name(self.room_id),
            {
                "type": "chat.message",
                "payload": {
                    'chat_id': self.room_id,
                    'content': message,
                    'username': self.user.username,
                }
            }
        )

    async def add_member(self, payload: FrontendAddMemberPayload):
        member = await atry_get_member_from_user_room(self.user, payload["chat_id"])

        if member is None:
            raise Exception("User not in room")

        new_member: Member = await aadd_user_to_room(payload["chat_id"],
                                                     payload["user_id"],
                                                     member)

        await self.channel_layer.group_send(
            get_user_group_name(new_member.user_id),
            {
                "type": "chat.add",
                "payload": payload
            }
        )

    # Receive message from room group
    async def chat_message(self, event: GroupEvent[GroupChatSendPayload]):
        payload = event["payload"]
        # Send message to WebSocket
        await self.send_json({
            'type': 'chat.message',
            'payload': payload
        })

    async def chat_add(self, event: GroupEvent[GroupChatAddPayload]):
        payload = event["payload"]
        # Send message to WebSocket
        await self.send_json({
            'type': 'chat.add',
            'payload': payload
        })


def get_room_group_name(room_id: int) -> str:
    return f"chat_{room_id}"


def get_user_group_name(user_id: int) -> str:
    return f"user_{user_id}"


@database_sync_to_async
def atry_get_member_from_user_room(user: User, room_id: id):
    return try_get_member_from_user_room(user, room_id)


@database_sync_to_async
def aadd_user_to_room(room_id: int,
                      user_id: int,
                      adding_member: Member) -> Member:
    return add_user_to_room(room_id, user_id, adding_member)


@database_sync_to_async
def asave_message(member, content):
    return Message.objects.create(member=member, content=content)
