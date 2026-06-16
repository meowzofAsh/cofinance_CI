from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    Conversation entre un client et un agent.
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (OPEN, "Ouverte"),
        (CLOSED, "Fermée"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_conversations",
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_conversations",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=OPEN,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conversation {self.id}"

    @property
    def last_message(self):
        return self.messages.order_by("-sent_at").first()

    @property
    def agent_name(self):
        return self.agent.get_full_name() or self.agent.username if self.agent else "Non assigné"

    @property
    def client_name(self):
        return self.client.get_full_name() or self.client.username


class Message(models.Model):
    """
    Messages d'une conversation.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    content = models.TextField()

    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"Message {self.id}"