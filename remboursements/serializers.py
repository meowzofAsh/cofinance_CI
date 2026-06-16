from rest_framework import serializers

from .models import Remboursement, RepaymentSchedule


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    days_late = serializers.ReadOnlyField()
    penalty = serializers.ReadOnlyField()
    remaining = serializers.ReadOnlyField()

    class Meta:
        model = RepaymentSchedule
        fields = [
            "id",
            "credit",
            "due_date",
            "amount_due",
            "amount_paid",
            "status",
            "days_late",
            "penalty",
            "remaining",
            "paid_at",
        ]
        read_only_fields = [
            "id", "credit", "amount_due", "status",
            "days_late", "penalty", "remaining", "paid_at",
        ]


class RemboursementSerializer(serializers.ModelSerializer):
    schedule_detail = RepaymentScheduleSerializer(
        source="schedule", read_only=True
    )

    class Meta:
        model = Remboursement
        fields = [
            "id",
            "credit",
            "schedule",
            "schedule_detail",
            "amount_paid",
            "payment_date",
            "penalty",
            "comments",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "penalty",
            "created_at",
            "schedule_detail",
        ]

    def create(self, validated_data):
        remboursement = Remboursement(**validated_data)
        remboursement.penalty = remboursement.calculate_penalty()
        remboursement.save()

        if remboursement.schedule:
            sched = remboursement.schedule
            sched.amount_paid += remboursement.amount_paid
            if sched.amount_paid >= sched.amount_due:
                sched.status = RepaymentSchedule.PAYEE
                sched.paid_at = remboursement.payment_date
            sched.save()

        return remboursement


class RemboursementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remboursement
        fields = [
            "id",
            "amount_paid",
            "payment_date",
            "penalty",
            "comments",
        ]
