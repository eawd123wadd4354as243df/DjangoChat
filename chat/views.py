from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render

from chat.forms import CreateServerForm, AddMemberForm
from chat.models import Member, Room, Message


@login_required
def index(request):
    if request.method == "POST":
        create_server_form = create_room(request)
    else:
        create_server_form = CreateServerForm(),

    user_rooms = Room.objects.filter(members=request.user)

    context = {
        "rooms": user_rooms,
        "members": [],
        "room_name": "Select a Room",
        "create_server_form": create_server_form,
    }

    return render(request, "chat/main.html", context)


@login_required
def room(request, room_id):
    if request.method == "POST":
        create_server_form = create_room(request)
        add_member_form = add_member(request, room_id)
    else:
        create_server_form = CreateServerForm()
        add_member_form = AddMemberForm()

    room = get_object_or_404(Room, pk=room_id)

    if not room.members.filter(pk=request.user.pk).exists():
        return HttpResponseNotFound("Could not find room.")

    members = Member.objects.filter(room=room).select_related("user")
    user_rooms = Room.objects.filter(members=request.user)

    messages = Message.objects.filter(member__room_id=room.id).select_related("member__user")

    context = {
        "room_id": room.id,
        "room_name": room.name,
        "members": members,
        "rooms": user_rooms,
        "create_server_form": create_server_form,
        "add_member_form": add_member_form,
        "messages": messages,
    }

    return render(request, "chat/main.html", context)


def create_room(request) -> CreateServerForm:
    # todo use this in template as well
    form = CreateServerForm(request.POST)

    if form.is_valid():
        new_room = Room.objects.create(name=form.cleaned_data["server_name"])
        new_member = Member.objects.create(room=new_room, user=request.user)

    return form


def add_member(request, room_id: int) -> AddMemberForm:
    form = AddMemberForm(request.POST)
    if form.is_valid():
        user = User.objects.get(username=form.cleaned_data["user_name"])

        if Member.objects.filter(room=room_id, user=user).exists():
            return form

        new_member = Member.objects.create(room_id=room_id, user=user)

    return form
