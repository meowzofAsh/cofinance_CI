from django.contrib import admin

from .models import (
    InsuranceProduct,
    InsuranceSubscription,
)


@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "duration_days",
        "created_at",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


@admin.register(InsuranceSubscription)
class InsuranceSubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "client",
        "product",
        "start_date",
        "end_date",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "client__username",
        "product__name",
    )

    ordering = (
        "-created_at",
    )