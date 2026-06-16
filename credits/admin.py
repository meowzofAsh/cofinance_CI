# credits/admin.py

from django.contrib import admin

from .models import Credit


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    """
    Administration des microcrédits
    """

    list_display = (
        "id",
        "client",
        "amount",
        "approved_amount",
        "duration",
        "status",
        "eligibility_score",
        "interest_rate",
        "created_at",
    )

    list_filter = (
        "status",
        "duration",
        "created_at",
    )

    search_fields = (
        "client__username",
        "client__email",
        "purpose",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "eligibility_score",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Informations générales",
            {
                "fields": (
                    "client",
                    "amount",
                    "duration",
                    "purpose",
                    "monthly_income",
                    "supporting_document",
                )
            },
        ),

        (
            "Analyse",
            {
                "fields": (
                    "eligibility_score",
                    "status",
                    "approved_amount",
                    "interest_rate",
                    "repayment_start_date",
                    "notes",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )