from django.db.models.signals import post_save
from django.dispatch import receiver

from credits.models import Credit
from .models import generate_repayment_schedules


@receiver(post_save, sender=Credit)
def generate_schedules_on_disbursement(sender, instance, created, raw, **kwargs):
    if raw:
        return
    if instance.status == Credit.DECAISSEE and not instance.schedules.exists():
        generate_repayment_schedules(instance)
