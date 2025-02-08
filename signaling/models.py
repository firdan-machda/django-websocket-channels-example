import uuid
from django.db import models


class WebRTCSession(models.Model):
    session_uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    alias = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WebRTCUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class WebRTCOffer(models.Model):
    webrtc_session = models.ForeignKey(WebRTCSession, on_delete=models.CASCADE)
    user = models.ForeignKey(WebRTCUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, default="offer")
    offer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + str(self.webrtc_session.session_uuid)