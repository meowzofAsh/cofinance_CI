from rest_framework import generics, permissions

from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationReadSerializer,
)


class NotificationListView(generics.ListAPIView):
    """
    Liste des notifications de l'utilisateur connecté
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Détail d'une notification
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )


class NotificationReadView(generics.UpdateAPIView):
    """
    Marquer une notification comme lue
    """

    serializer_class = NotificationReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(is_read=True)