from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_view, name="chat-index"),
    path("chat/<username>", views.get_or_create_chatroom, name="start-chat"),
    path("room/<chatroom_name>", views.chat_view, name="chatroom"),
    path("new_groupchat/", views.create_groupchat, name="new-groupchat"),
    path(
        "edit/<chatroom_name>",
        views.chatroom_edit_view,
        name="edit-chatroom",
    ),
    path(
        "delete/<chatroom_name>",
        views.chatroom_delete_view,
        name="chatroom-delete",
    ),
    path(
        "leave/<chatroom_name>",
        views.chatroom_leave_view,
        name="chatroom-leave",
    ),
    path(
        "fileupload/<chatroom_name>",
        views.chat_file_upload,
        name="chat-file-upload",
    ),
]
