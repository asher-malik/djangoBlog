from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

from .models import Token
import os

def generate_token(email):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    token = serializer.dumps(email, salt='django-python')
    token_data = Token.objects.create(token=token, email=email)
    token_data.save()
    return token

def confirm_token(token, expiration=1800):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(
            token, salt='django-python', max_age=expiration
        )
        token_data = Token.objects.get(email=email, token=token)
        if token_data.used:
            return False
        return email
    except:
        return False
    

def send_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    mail_subject = mail_subject
    message = render_to_string(email_template, {
        'user': user,
        'protocal': 'https' if request.is_secure() else 'http',
        'domain': current_site,
        'token': generate_token(user.email),
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, to=[to_email], from_email=from_email)
    mail.send()