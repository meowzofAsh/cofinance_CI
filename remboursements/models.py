from decimal import Decimal
from datetime import date

from django.db import models
from django.utils import timezone

from credits.models import Credit


class RepaymentSchedule(models.Model):
    EN_ATTENTE = "EN_ATTENTE"
    PAYEE = "PAYEE"
    RETARD = "RETARD"

    STATUS_CHOICES = [
        (EN_ATTENTE, "En attente"),
        (PAYEE, "Payée"),
        (RETARD, "En retard"),
    ]

    credit = models.ForeignKey(
        Credit,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    due_date = models.DateField()

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant dû",
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Montant payé",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=EN_ATTENTE,
    )

    paid_at = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["due_date"]
        verbose_name = "Échéance"
        verbose_name_plural = "Échéances"

    def __str__(self):
        return f"Échéance #{self.id} - Crédit #{self.credit.pk} - {self.due_date}"

    @property
    def days_late(self):
        if self.status == self.PAYEE:
            return 0
        today = date.today()
        delta = (today - self.due_date).days
        return max(0, delta)

    @property
    def penalty(self):
        if self.days_late <= 0:
            return Decimal("0.00")
        rate = Decimal("0.01")
        return (self.amount_due - self.amount_paid) * rate * Decimal(str(self.days_late))

    @property
    def remaining(self):
        return self.amount_due - self.amount_paid


class Remboursement(models.Model):
    """
    Enregistrement des remboursements d'un crédit.
    """

    credit = models.ForeignKey(
        Credit,
        on_delete=models.CASCADE,
        related_name="remboursements",
    )

    schedule = models.ForeignKey(
        RepaymentSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Échéance concernée",
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_date = models.DateField()

    penalty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    comments = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Remboursement"
        verbose_name_plural = "Remboursements"

    def __str__(self):
        return f"Remboursement #{self.id}"

    def calculate_penalty(self):
        if self.schedule:
            return self.schedule.penalty
        return Decimal("0.00")


def generate_repayment_schedules(credit):
    """
    Génère les échéances pour un crédit décaissé.
    Amortissement linéaire avec intérêts compris.
    """
    start_date = credit.repayment_start_date or date.today()
    duration = credit.duration
    amount = credit.approved_amount or credit.amount
    rate = Decimal(str(credit.interest_rate))

    total_interest = amount * rate / Decimal("100") * Decimal(duration) / Decimal("12")
    total_to_pay = amount + total_interest
    monthly_payment = total_to_pay / Decimal(duration)

    schedules = []
    for i in range(duration):
        month = (start_date.month - 1 + (i + 1)) % 12
        year = start_date.year + (start_date.month - 1 + (i + 1)) // 12
        if month == 0:
            month = 12
            year -= 1
        try:
            due_date = start_date.replace(year=year, month=month)
        except ValueError:
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            due_date = start_date.replace(year=year, month=month, day=min(start_date.day, last_day))

        schedules.append(
            RepaymentSchedule(
                credit=credit,
                due_date=due_date,
                amount_due=monthly_payment.quantize(Decimal("0.01")),
            )
        )

    RepaymentSchedule.objects.bulk_create(schedules)
