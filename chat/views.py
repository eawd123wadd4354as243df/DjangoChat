from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render

from chat.db import try_get_member_from_user_room


# Create your views here.

@login_required
def index(request):
    return render(request, "chat/index.html", {'user': request.user})

@login_required
def room(request, room_id):
    member = try_get_member_from_user_room(request.user, room_id)

    if member is None:
        return HttpResponseNotFound('Could not find room.')

    return render(request, "chat/room.html", {"room_id": room_id})

