from django.contrib import admin
from .models import WebRTCSession, WebRTCUser, WebRTCChatMessage


@admin.register(WebRTCSession)
class WebRTCSessionAdmin(admin.ModelAdmin):
    list_display = ('session_uuid', 'created_at')


@admin.register(WebRTCUser)
class WebRTCUserAdmin(admin.ModelAdmin):
    list_display = ('webrtc_session', 'user', 'joined')


@admin.register(WebRTCChatMessage)
class WebRTCChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_session', 'user', 'created_at')
