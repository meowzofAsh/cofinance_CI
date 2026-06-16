from rest_framework import serializers

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "sender_id", "content", "sent_at"]
        read_only_fields = ["id", "sender", "sender_id", "sent_at"]

    def create(self, validated_data):
        request = self.context["request"]
        return Message.objects.create(
            sender=request.user,
            **validated_data,
        )


class ConversationSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    client_id = serializers.IntegerField(source="client.id", read_only=True)
    agent = serializers.StringRelatedField()
    agent_id = serializers.IntegerField(source="agent.id", read_only=True, allow_null=True)
    last_message = serializers.SerializerMethodField()
    client_online = serializers.BooleanField(source="client.is_online", read_only=True)
    agent_online = serializers.BooleanField(source="agent.is_online", read_only=True, allow_null=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "client",
            "client_id",
            "agent",
            "agent_id",
            "status",
            "created_at",
            "updated_at",
            "last_message",
            "client_online",
            "agent_online",
        ]
        read_only_fields = ["id", "client", "created_at", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.last_message
        if msg:
            return {
                "content": msg.content[:80],
                "sent_at": msg.sent_at,
            }
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = []

    def create(self, validated_data):
        request = self.context["request"]
        return Conversation.objects.create(
            client=request.user,
            **validated_data,
        )
