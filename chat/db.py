from django.contrib.auth.models import User

from chat.models import Member


def try_get_member_from_user_room(user: User, room_id: id):
    try:
        return Member.objects.get(user=user, room__id=room_id)
    except Member.DoesNotExist:
        return None
