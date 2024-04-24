from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from celery import shared_task


@shared_task
def send_verification_email(user_id):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=user_id)
        send_mail(
            'Verify your  account',
            'Follow this link to verify your account. '
            'The link will be active within 24 hours: '
            'http://localhost:8000%s' % reverse(
                viewname='verify',
                kwargs={'uuid': str(user.verification_uuid)}),
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except UserModel.DoesNotExist:
        pass


@shared_task
def update_user_status(user_id, statys):
    UserModel = get_user_model()
    user = UserModel.objects.get(pk=user_id)
    user.is_online = statys
    user.save()

