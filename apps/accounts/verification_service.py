from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import (
    VerificationToken,
)


def create_verification_token(user):
    """
    Creates or renews the verification token for a user.
    """
    token = VerificationToken.objects.create(
        user=user,
        expiration=timezone.now() + timedelta(minutes=5),
        used=False,
    )

    return token.uuid


def send_verification_email(request, user):
    """
    Creates the verification token and sends the email.
    """
    token = create_verification_token(user)

    verify_url = request.build_absolute_uri(
        reverse(
            "verify-account",
            args=[token],
        )
    )

    message = f"""
Hola {user.first_name},

Bienvenido a Sky App.

Para activar tu cuenta debes ingresar al siguiente enlace:

{verify_url}

Este enlace expirará en 5 minutos.

Si no solicitaste este registro puedes ignorar este correo.

Sky App
"""
    try:
        send_mail(
            subject="Verificación de cuenta",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                user.email
            ],
        )
        return True
    except:
        return False