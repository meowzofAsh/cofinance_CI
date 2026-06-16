from django.db.models.signals import post_save
from django.dispatch import receiver

from credits.models import Credit
from assurances.models import InsuranceSubscription
from support_chat.models import Conversation
from .models import NPSSurvey


@receiver(post_save, sender=Credit)
def create_nps_context_credit(sender, instance, created, **kwargs):
    if instance.status == Credit.DECAISSEE and not created:
        NPSSurvey.objects.get_or_create(
            user=instance.client,
            context_type="CREDIT",
            context_id=instance.pk,
            defaults={"score": 0, "comment": ""},
        )


@receiver(post_save, sender=InsuranceSubscription)
def create_nps_context_insurance(sender, instance, created, **kwargs):
    if not created:
        return
    NPSSurvey.objects.get_or_create(
        user=instance.client,
        context_type="ASSURANCE",
        defaults={"score": 0, "comment": ""},
    )


@receiver(post_save, sender=Conversation)
def create_nps_context_chat(sender, instance, created, **kwargs):
    if instance.status == Conversation.CLOSED and not created:
        NPSSurvey.objects.get_or_create(
            user=instance.client,
            context_type="CHAT",
            context_id=instance.pk,
            defaults={"score": 0, "comment": ""},
        )
