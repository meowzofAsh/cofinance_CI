# credits/models.py

from decimal import Decimal
from django.conf import settings
from django.db import models


class Credit(models.Model):
    """
    Modèle représentant une demande de microcrédit.
    """

    SOUMISE = "SOUMISE"
    EN_ANALYSE = "EN_ANALYSE"
    APPROUVEE = "APPROUVEE"
    REJETEE = "REJETEE"
    DECAISSEE = "DECAISSEE"

    STATUS_CHOICES = [
        (SOUMISE, "Soumise"),
        (EN_ANALYSE, "En analyse"),
        (APPROUVEE, "Approuvée"),
        (REJETEE, "Rejetée"),
        (DECAISSEE, "Décaissée"),
    ]

    DURATION_CHOICES = [
        (3, "3 mois"),
        (6, "6 mois"),
        (12, "12 mois"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credits",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    duration = models.IntegerField(
        choices=DURATION_CHOICES,
    )

    purpose = models.TextField()

    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    supporting_document = models.FileField(
        upload_to="credits/documents/",
        blank=True,
        null=True,
    )

    eligibility_score = models.IntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=SOUMISE,
    )

    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00"),
    )

    repayment_start_date = models.DateField(
        blank=True,
        null=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Microcrédit"
        verbose_name_plural = "Microcrédits"

    def __str__(self):
        return f"Crédit #{self.id} - {self.client.username}"

    def calculate_eligibility_score(self):
        """
        Calcul simplifié du score d'éligibilité.
        """

        score = 50

        if self.monthly_income >= self.amount:
            score += 30

        elif self.monthly_income >= (self.amount / 2):
            score += 15

        if self.duration <= 6:
            score += 20

        return min(score, 100)