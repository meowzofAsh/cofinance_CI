from django.db.models.signals import post_save
from django.dispatch import receiver

from credits.models import Credit
from remboursements.models import Remboursement
from assurances.models import InsuranceSubscription
from .models import Notification


@receiver(post_save, sender=Credit)
def notify_credit_status_change(sender, instance, created, raw, **kwargs):
    if raw:
        return
    if created:
        Notification.objects.create(
            user=instance.client,
            title="Demande de crédit soumise",
            message=(
                f"Votre demande de crédit #{instance.pk} "
                f"d'un montant de {instance.amount} F CFA a été soumise avec succès. "
                f"Score d'éligibilité : {instance.eligibility_score}/100."
            ),
        )
        return

    old_status = None
    if instance.pk:
        try:
            old = Credit.objects.get(pk=instance.pk)
            old_status = old.status
        except Credit.DoesNotExist:
            pass

    if old_status and old_status != instance.status:
        statuts_labels = dict(Credit.STATUS_CHOICES)
        messages_map = {
            Credit.EN_ANALYSE: (
                f"Votre demande de crédit #{instance.pk} est en cours d'analyse."
            ),
            Credit.APPROUVEE: (
                f"Félicitations ! Votre demande de crédit #{instance.pk} "
                f"a été approuvée pour un montant de {instance.approved_amount} F CFA."
            ),
            Credit.REJETEE: (
                f"Votre demande de crédit #{instance.pk} n'a pas été retenue. "
                f"Vous pouvez soumettre une nouvelle demande."
            ),
            Credit.DECAISSEE: (
                f"Votre crédit #{instance.pk} a été décaissé ! "
                f"Le remboursement commence le {instance.repayment_start_date}."
            ),
        }

        titre = f"Statut du crédit #{instance.pk} : {statuts_labels.get(instance.status, instance.status)}"
        message = messages_map.get(
            instance.status,
            f"Le statut de votre crédit #{instance.pk} est passé à "
            f"\"{statuts_labels.get(instance.status, instance.status)}\"."
        )

        Notification.objects.create(
            user=instance.client,
            title=titre,
            message=message,
        )


@receiver(post_save, sender=Remboursement)
def notify_repayment(sender, instance, created, raw, **kwargs):
    if raw or not created:
        return

    total_paye = sum(
        r.amount_paid for r in instance.credit.remboursements.all()
    )
    reste = instance.credit.amount - total_paye

    titre = f"Remboursement enregistré — Crédit #{instance.credit.pk}"
    message = (
        f"Un paiement de {instance.amount_paid} F CFA a été enregistré "
        f"sur votre crédit #{instance.credit.pk}. "
        f"Reste à payer : {reste} F CFA."
    )

    Notification.objects.create(
        user=instance.credit.client,
        title=titre,
        message=message,
    )


@receiver(post_save, sender=InsuranceSubscription)
def notify_insurance_subscription(sender, instance, created, raw, **kwargs):
    if raw:
        return
    if created:
        titre = "Souscription confirmée"
        message = (
            f"Votre souscription à l'assurance \"{instance.product.name}\" "
            f"a été confirmée. Valable du {instance.start_date} au {instance.end_date}."
        )
    else:
        titre = "Mise à jour de votre souscription"
        message = (
            f"Votre souscription à l'assurance \"{instance.product.name}\" "
            f"est maintenant {dict(instance.STATUS_CHOICES).get(instance.status, instance.status)}."
        )

    Notification.objects.create(
        user=instance.client,
        title=titre,
        message=message,
    )
