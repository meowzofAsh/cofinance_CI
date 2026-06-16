from django.contrib import admin

from .models import (
    Conversation,
    Message,
)


class MessageInline(admin.TabularInline):

    model = Message

    extra = 0

    readonly_fields = (
        "sender",
        "content",
        "sent_at",
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "client",
        "agent",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "client__username",
        "agent__username",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        MessageInline,
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "sender",
        "sent_at",
    )

    search_fields = (
        "sender__username",
        "content",
    )

    ordering = (
        "-sent_at",
    )