from django.contrib import admin
from .models import ChatSession, ChatUser, ChatMessage

# Register your models here.
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display=['session_uuid', 'created_at']


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display=['chat_session', 'user', 'joined']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display=['chat_session','user','created_at']