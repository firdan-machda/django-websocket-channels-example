from django.contrib import admin
from .models import WebRTCSession, WebRTCUser, WebRTCOffer

# Register your models here.


@admin.register(WebRTCSession)
class WebRTCSessionAdmin(admin.ModelAdmin):
    list_display = ('session_uuid', 'alias', 'created_at')
    search_fields = ('alias',)


@admin.register(WebRTCUser)
class WebRTCUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'joined')
    search_fields = ('username',)


@admin.register(WebRTCOffer)
class WebRTCOfferAdmin(admin.ModelAdmin):
    list_display = ('webrtc_session', 'user', 'created_at')
    search_fields = ('webrtc_session__alias', 'user__username')
