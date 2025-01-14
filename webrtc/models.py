from django.db import models
import uuid
from django.conf import settings

# Create your models here.


class WebRTCSession(models.Model):
    session_uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class WebRTCUser(models.Model):
    webrtc_session = models.ForeignKey(WebRTCSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.SET_NULL)
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('webrtc_session', 'user')


class WebRTCChatMessage(models.Model):
    chat_session = models.ForeignKey(WebRTCSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.SET_NULL)
    message = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
