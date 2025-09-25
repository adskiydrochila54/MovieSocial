from django.db import models
from django.conf import settings

class Chat(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chats"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        usernames = ", ".join([p.username for p in self.participants.all()])
        return f"Chat between {usernames}"

    def last_message(self):
        return self.messages.order_by("-created_at").first()


class DirectMessage(models.Model):
    chat = models.ForeignKey(
        Chat,
        related_name="messages",
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_messages",
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"From {self.sender.username}: {self.content[:20]}"
