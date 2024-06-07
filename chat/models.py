import uuid
from django.db import models
from django.conf import settings

# Create your models here.
class ChatSession(models.Model):
    session_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatUser(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat_session', 'user')


class ChatMessage(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    message = models.TextField(max_length=200)
