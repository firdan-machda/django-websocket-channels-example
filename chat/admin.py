from django.contrib import admin

from .models import ChatSession, ChatUser, ChatMessage
# Register your models here.
admin.site.register(ChatSession)
admin.site.register(ChatUser)
admin.site.register(ChatMessage)