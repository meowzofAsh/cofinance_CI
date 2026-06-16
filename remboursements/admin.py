from django.contrib import admin

from .models import Remboursement, RepaymentSchedule


@admin.register(Remboursement)
class RemboursementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "credit",
        "amount_paid",
        "payment_date",
        "penalty",
    )
    list_filter = ("payment_date",)
    search_fields = ("credit__client__username",)
    ordering = ("-payment_date",)
    readonly_fields = ("created_at",)


@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "credit",
        "due_date",
        "amount_due",
        "amount_paid",
        "status",
        "days_late",
    )
    list_filter = ("status", "due_date")
    search_fields = ("credit__client__username",)
    ordering = ("due_date",)
