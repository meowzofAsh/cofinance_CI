from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from credits.models import Credit
from remboursements.models import RepaymentSchedule
from assurances.models import InsuranceSubscription
from notifications.models import Notification


class Command(BaseCommand):
    help = "Vérifie les échéances en retard, les expirations d'assurance et envoie les notifications"

    def handle(self, *args, **options):
        today = date.today()
        notifications_crees = 0

        # --- Échéances en retard (J+1) ---
        hier = today - timedelta(days=1)
        overdue = RepaymentSchedule.objects.filter(
            due_date__lte=hier,
            status=RepaymentSchedule.EN_ATTENTE,
        )
        for sched in overdue:
            sched.status = RepaymentSchedule.RETARD
            sched.save()

            total_paye = sum(
                r.amount_paid for r in sched.credit.remboursements.all()
            )
            reste = sched.amount_due - sched.amount_paid

            Notification.objects.get_or_create(
                user=sched.credit.client,
                title=f"Retard de paiement — Crédit #{sched.credit.pk}",
                defaults={
                    "message": (
                        f"L'échéance du {sched.due_date} pour votre crédit "
                        f"#{sched.credit.pk} est en retard. "
                        f"Montant dû : {sched.amount_due} F CFA. "
                        f"Une pénalité de {sched.penalty} F CFA s'applique. "
                        f"Reste total à payer : {reste} F CFA."
                    ),
                },
            )
            notifications_crees += 1

        # --- Rappels J-3 avant échéance ---
        j3 = today + timedelta(days=3)
        upcoming = RepaymentSchedule.objects.filter(
            due_date=j3,
            status=RepaymentSchedule.EN_ATTENTE,
        )
        for sched in upcoming:
            Notification.objects.get_or_create(
                user=sched.credit.client,
                title=f"Rappel : Échéance dans 3 jours — Crédit #{sched.credit.pk}",
                defaults={
                    "message": (
                        f"Votre échéance de {sched.amount_due} F CFA "
                        f"pour le crédit #{sched.credit.pk} est due le "
                        f"{sched.due_date}. Merci de prévoir votre règlement."
                    ),
                },
            )
            notifications_crees += 1

        # --- Expiration assurance J-15 ---
        j15 = today + timedelta(days=15)
        expiring = InsuranceSubscription.objects.filter(
            end_date=j15,
            status=InsuranceSubscription.ACTIVE,
        )
        for sub in expiring:
            Notification.objects.get_or_create(
                user=sub.client,
                title=f"Expiration imminente : {sub.product.name}",
                defaults={
                    "message": (
                        f"Votre assurance \"{sub.product.name}\" expire le "
                        f"{sub.end_date}. Pensez à renouveler votre souscription "
                        f"pour continuer à bénéficier de votre couverture."
                    ),
                },
            )
            notifications_crees += 1

        # --- Expiration assurance J+0 (expirée) ---
        expired = InsuranceSubscription.objects.filter(
            end_date__lt=today,
            status=InsuranceSubscription.ACTIVE,
        )
        for sub in expired:
            sub.status = InsuranceSubscription.EXPIRED
            sub.save()

            Notification.objects.get_or_create(
                user=sub.client,
                title=f"Assurance expirée : {sub.product.name}",
                defaults={
                    "message": (
                        f"Votre assurance \"{sub.product.name}\" a expiré le "
                        f"{sub.end_date}. Souscrivez à nouveau pour être couvert."
                    ),
                },
            )
            notifications_crees += 1

        if notifications_crees:
            self.stdout.write(self.style.SUCCESS(
                f"{notifications_crees} notification(s) créée(s)."
            ))
        else:
            self.stdout.write("Aucune notification à créer.")
