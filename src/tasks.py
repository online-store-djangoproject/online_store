from celery import shared_task
from django.core.mail import send_mail

from django.conf import settings


@shared_task
def send_otp_email_task(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email], fail_silently=False)
