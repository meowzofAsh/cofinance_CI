from django.db import models
from django.conf import settings


class NPSSurvey(models.Model):
    CONTEXT_CHOICES = [
        ("CREDIT", "Crédit"),
        ("ASSURANCE", "Assurance"),
        ("CHAT", "Support client"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nps_surveys",
        verbose_name="Client",
    )
    score = models.IntegerField(
        verbose_name="Score NPS (0-10)",
        help_text="0 = Pas du tout satisfait, 10 = Extrêmement satisfait",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Commentaire",
        help_text="Avez-vous des suggestions ?",
    )
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_CHOICES,
        verbose_name="Contexte",
    )
    context_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="ID de référence",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de réponse",
    )

    class Meta:
        verbose_name = "Réponse NPS"
        verbose_name_plural = "Réponses NPS"
        ordering = ["-created_at"]

    def __str__(self):
        return f"NPS {self.score}/10 — {self.user.username} ({self.get_context_type_display()})"

    @property
    def category(self):
        if self.score >= 9:
            return "Promoteur"
        elif self.score >= 7:
            return "Passif"
        return "Détracteur"

    @property
    def category_class(self):
        if self.score >= 9:
            return "badge-success"
        elif self.score >= 7:
            return "badge-warning"
        return "badge-danger"
