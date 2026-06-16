from django.conf import settings
from django.db import models


class InsuranceProduct(models.Model):
    """
    Catalogue des produits d'assurance
    """

    name = models.CharField(
        max_length=100
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    duration_days = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Produit d'assurance"
        verbose_name_plural = "Produits d'assurance"

    def __str__(self):
        return self.name


class InsuranceSubscription(models.Model):
    """
    Souscription d'un client
    """

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (EXPIRED, "Expirée"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    product = models.ForeignKey(
        InsuranceProduct,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Souscription"
        verbose_name_plural = "Souscriptions"

    def __str__(self):
        return f"{self.client} - {self.product}"