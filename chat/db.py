from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from chat.models import Member


@database_sync_to_async
def try_get_member_from_user_room(user: User, room_id: int):
    try:
        return Member.objects.get(user=user, room__id=room_id)
    except Member.DoesNotExist:
        return None
