from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatGroup, GroupMessage
from .forms import ChatmessageCreateForm, NewGroupForm, ChatRoomEditForm


@login_required
def chat_view(request, chatroom_name="public-chat"):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(
                    request, "You need to verify your email to join the chat!"
                )
                return redirect("users:profile-settings")

    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid:
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            template_name = "chat/partials/chat_message.html"
            context = {
                "message": message,
                "user": request.user,
            }
            return render(
                request, template_name=template_name, context=context
            )
    template_name = "chat/index.html"
    context = {
        "chat_messages": chat_messages,
        "form": form,
        "other_user": other_user,
        "chatroom_name": chatroom_name,
        "chat_group": chat_group,
    }

    return render(request, template_name=template_name, context=context)


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect("chat:chat-index")

    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)
    return redirect("chat:chatroom", chatroom.group_name)


@login_required
def create_groupchat(request):
    form = NewGroupForm()

    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect("chat:chatroom", new_groupchat.group_name)
    template_name = "chat/create_groupchat.html"

    context = {"form": form}
    return render(request, template_name=template_name, context=context)


@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    form = ChatRoomEditForm(instance=chat_group)

    if request.method == "POST":
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist("remove_members")
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)

            return redirect("chat:chatroom", chatroom_name)
    template_name = "chat/chatroom_edit.html"
    context = {"form": form, "chat_group": chat_group}
    return render(request, template_name=template_name, context=context)


@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    if request.method == "POST":
        chat_group.delete()
        messages.success(request, "Chatroom deleted")
        return redirect("chat:chat-index")
    template_name = "chat/chatroom_delete.html"
    context = {"chat_group": chat_group}
    return render(request, template_name=template_name, context=context)


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()

    if request.method == "POST":
        chat_group.members.remove(request.user)
        messages.success(request, "You left the Chat")
        return redirect("chat:chat-index")


def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES["file"]
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
        )
        channel_layer = get_channel_layer()
        event = {
            "type": "message_handler",
            "message_id": message.id,
        }
        async_to_sync(channel_layer.group_send)(chatroom_name, event)
    return HttpResponse()
