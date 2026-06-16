from django.urls import path

from .views import (
    ConversationCreateView,
    ConversationListView,
    MessageListView,
    assign_conversation,
    close_conversation,
)

urlpatterns = [
    # Créer une conversation
    path("", ConversationCreateView.as_view(), name="conversation-create"),
    # Liste
    path("list/", ConversationListView.as_view(), name="conversation-list"),
    # Messages
    path("<int:pk>/messages/", MessageListView.as_view(), name="message-list"),
    # Assigner un agent
    path("<int:pk>/assign/", assign_conversation, name="api_chat_assign"),
    # Fermer une conversation
    path("<int:pk>/close/", close_conversation, name="api_chat_close"),
]
