from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.tasks import send_verification_email
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def user_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_verified:
        send_verification_email.delay(instance.pk)
