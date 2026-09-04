from datetime import timedelta
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    document = models.IntegerField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}"
    
    def status(self):
        if not self.is_verified:
            return "No verificado"
        if not self.is_active:
            return "Inactivo"
        return "Activo"


class VerificationStatus:

    VERIFIED = "verified"
    SUCCESS = "success"
    EXPIRED = "expired"
    NOT_FOUND = "not_found"


class VerificationToken(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    expiration = models.DateTimeField()
    
    used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    def save(self, *args, **kwargs):

        if not self.expiration:
            self.expiration = (
                timezone.now() +
                timedelta(minutes=5)
            )

        super().save(*args, **kwargs)
    
    @property
    def expired(self):
        return timezone.now() > self.expiration
    
    def verify(self, request):
        from .verification_service import send_verification_email

        if self.used:
            return {"response": False, "status": VerificationStatus.VERIFIED}

        if self.expired:
            send_verification_email(request, self.user)
            return {"response": False, "status": VerificationStatus.EXPIRED}

        self.user.is_verified = True
        self.user.save(
            update_fields=["is_verified"]
        )
        
        self.used = True
        self.verified_at = timezone.now()

        self.delete()

        return {"response": True, "status": VerificationStatus.SUCCESS}
