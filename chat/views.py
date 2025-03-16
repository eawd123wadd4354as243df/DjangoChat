from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render

from chat.db import try_get_member_from_user_room
from chat.models import Member, Room


@login_required
def index(request):
    user_rooms = Room.objects.filter(members=request.user)

    context = {
        "rooms": user_rooms,
        "members": [],
        "room_name": "Select a Room",
    }

    return render(request, "main.html", context)


@login_required
def room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if not room.members.filter(pk=request.user.pk).exists():
        return HttpResponseNotFound("Could not find room.")

    members = Member.objects.filter(room=room).select_related("user")
    user_rooms = Room.objects.filter(members=request.user)

    context = {
        "room_id": room.id,
        "room_name": room.name,
        "members": members,
        "rooms": user_rooms,
    }

    return render(request, "main.html", context)
