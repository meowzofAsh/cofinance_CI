# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé
    """

    CLIENT = "CLIENT"
    AGENT = "AGENT"
    ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (CLIENT, "Client"),
        (AGENT, "Agent de terrain"),
        (ADMIN, "Administrateur"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENT,
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    address = models.TextField(
        blank=True,
        null=True,
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    is_online = models.BooleanField(
        default=False,
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_client(self):
        return self.role == self.CLIENT

    @property
    def is_agent(self):
        return self.role == self.AGENT

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN

    @property
    def notifications_count(self):
        from notifications.models import Notification
        return Notification.objects.filter(user=self, is_read=False).count()
