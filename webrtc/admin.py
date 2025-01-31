from django.contrib import admin
from .models import WebRTCSession, WebRTCUser, WebRTCChatMessage


class WebRTCUserInline(admin.TabularInline):
    model = WebRTCUser
    extra = 0


@admin.register(WebRTCSession)
class WebRTCSessionAdmin(admin.ModelAdmin):
    list_display = ('session_uuid', 'alias', 'created_at')
    inlines = [WebRTCUserInline]


@admin.register(WebRTCUser)
class WebRTCUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'joined')


@admin.register(WebRTCChatMessage)
class WebRTCChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = []
