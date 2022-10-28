from twilio.rest import Client
import random, string
from rest_framework.response import Response
from rest_framework import status
from .models import User, VerificationCode
from twilio.rest import Client
from django.conf import settings
from decouple import config
from Otp_projectAPI.celery import app
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


def create_code():
    return ''.join(random.choices(string.digits, k=6))

@shared_task
def create_VerificationCode(id, code):
    u=User.objects.filter(id=id)
    VerificationCode.objects.create(user=u.last(), code=code)


@shared_task
def send_verification_code(id, code):
    u=User.objects.filter(id=id)
    phonenumber=u.last().phonenumber
    client=Client(config('ACCOUNT_SID'), config('AUTH_TOKEN'))
    client.messages.create(
    body=f'Your otp verification code {code}',
    from_=config('ACCOUNT_PHONENUMBER'),
    to=str(phonenumber)
)

@shared_task
def verify_phonenumber(id):
    u=User.objects.filter(id=id)
    user=u.last()
    user.phonenumber_verified=True
    user.save()

@shared_task
def delete_invalid_codes():
    x= VerificationCode.objects.filter(date__lt=timezone.now() - timedelta(minutes=15) )
    if x.exists():
        for i in x:
            i.delete()


