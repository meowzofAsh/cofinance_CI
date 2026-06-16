from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
)


class ConversationCreateView(generics.CreateAPIView):
    """
    Créer une conversation
    """

    serializer_class = ConversationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}


class ConversationListView(generics.ListAPIView):
    """
    Liste des conversations
    """

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "AGENT"]:
            return Conversation.objects.all().order_by("-created_at")
        return Conversation.objects.filter(client=user).order_by("-created_at")


class MessageListView(generics.ListAPIView):
    """
    Historique des messages
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["pk"]
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by("sent_at")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def assign_conversation(request, pk):
    """
    Assigner un agent à une conversation
    """
    if request.user.role not in ["ADMIN", "AGENT"]:
        return Response(
            {"detail": "Permission refusée."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(
            {"detail": "Conversation introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    conv.agent = request.user
    conv.save()

    return Response({
        "detail": f"Conversation #{pk} assignée à {request.user.username}.",
        "agent": request.user.username,
    })


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def close_conversation(request, pk):
    """
    Fermer une conversation
    """
    if request.user.role not in ["ADMIN", "AGENT"]:
        return Response(
            {"detail": "Permission refusée."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(
            {"detail": "Conversation introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    conv.status = Conversation.CLOSED
    conv.save()

    return Response({
        "detail": f"Conversation #{pk} fermée.",
    })
