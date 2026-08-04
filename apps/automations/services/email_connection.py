from django.conf import settings
from django.core.mail import get_connection


def get_email_connection():
    """
    Retorna una conexión SMTP abierta utilizando la configuración
    definida en Django.
    """

    connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
    )

    connection.open()

    return connection