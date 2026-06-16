from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:

        model = Notification

        fields = [
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class NotificationReadSerializer(serializers.ModelSerializer):
    """
    Marquer une notification comme lue.
    """

    class Meta:

        model = Notification

        fields = [
            "is_read",
        ]