from django.contrib import admin

from .models import NPSSurvey


@admin.register(NPSSurvey)
class NPSSurveyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "score",
        "category",
        "context_type",
        "context_id",
        "created_at",
    )
    list_filter = ("score", "context_type", "created_at")
    search_fields = ("user__username", "user__email", "comment")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            "Réponse",
            {
                "fields": (
                    "user",
                    "score",
                    "comment",
                )
            },
        ),
        (
            "Contexte",
            {
                "fields": (
                    "context_type",
                    "context_id",
                )
            },
        ),
        (
            "Date",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )
