from apps.accounts.models import CustomUser

from django.db import models
from django.db.models import Max

class Customer(models.Model):
    
    MORA_DAYS = 80
    ACTIVE = "Asociado Activo"
    INACTIVE = "No asociado"
    
    ACTIVE_PARAM = "active"
    INACTIVE_PARAM = "inactive"
    MORA_PARAM = "mora"

    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        INACTIVE = "inactive", "Inactivo"
        MORA = "mora", "En mora"
        PENDING = "pending", "Pendiente"
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document = models.CharField(max_length=50)
    # type_document = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    type_customer = models.CharField(max_length=100, null=True, blank=True)
    nomina_name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    score = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    contributions = models.IntegerField(null=True, blank=True)
    test = models.BooleanField(default=False)
    
    @property
    def phone_num(self):
        if not self.phone:
            return None

        return int(float(self.phone))
    
    @property
    def active(self):
        return self.status == "Asociado Activo"
    
    @property
    def inactive(self):
        return self.status == "No asociado"
    
    @property
    def has_mora(self):
        return self.obligations.filter(
            mora_days__gt=self.MORA_DAYS
        ).exists()

    @property
    def status_label(self):
        if self.has_mora and self.active:
            return "Mora"

        if self.has_mora and self.inactive:
            return "Inactivo - Mora"

        if self.active:
            return "Activo"

        return "Inactivo"
    
    @property
    def status_color(self):

        if self.has_mora:
            return "warning"

        if self.active:
            return "success"

        if self.inactive:
            return "error"

        return "info"
    
    @property
    def mora_days(self):
        return (
            self.obligations.aggregate(
                max_days=Max("mora_days")
            )["max_days"] or 0
        )
    
    @classmethod
    def get_test_customer(cls):
        """
        Returns the test customer. If it does not exist, it is created
        together with a test obligation.
        """
        customer, _ = cls.objects.get_or_create(
            test=True,
            defaults={
                "first_name": "Usuario",
                "last_name": "Prueba",
                "document": "TEST-0001",
                "email": "test@example.com",
                "status": cls.ACTIVE,
                "type_customer": "Prueba",
                "nomina_name": "Prueba",
                "age": 30,
                "gender": "M",
                "phone": "3000000000",
                "score": "A",
                "city": "Bogotá",
                "contributions": "1222222",
            },
        )

        Obligations.objects.get_or_create(
            customer=customer,
            num_obligacion="TEST-001",
            defaults={
                "credit_line": "Prueba",
                "mora_days": 15,
                "total": "100000",
            },
        )

        return customer

    
class Obligations(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="obligations"
    )
    
    num_obligacion = models.CharField(max_length=100)
    credit_line = models.CharField(max_length=100, null=True, blank=True)
    mora_days = models.IntegerField(null=True, blank=True)
    total = models.CharField(max_length=100, null=True, blank=True)
    
    @property
    def mora_status(self):
        return self.mora_days > Customer.MORA_DAYS
    
    @property
    def total_formatted(self):
        try:
            value = int(''.join(filter(str.isdigit, self.total)))
            return f"$ {value:,}".replace(",", ".")
        except (TypeError, ValueError):
            return "$ 0"
    
    
class CustomerLog(models.Model):

    class Action(models.TextChoices):
        CUSTOMER_CREATED = "customer_created", "Asociado creado"
        CUSTOMER_UPDATED = "customer_updated", "Asociado actualizado"
        OBLIGATION_CREATED = "obligation_created", "Obligación creada"
        OBLIGATION_UPDATED = "obligation_updated", "Obligación actualizada"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )

    description = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(auto_now_add=True)


class ImportExecution(models.Model):

    class Type(models.TextChoices):
        CUSTOMERS = "customers", "Asociados"
        OBLIGATIONS = "obligations", "Obligaciones"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PROCESSING = "processing", "Procesando"
        SUCCESS = "success", "Completada"
        FAILED = "failed", "Fallida"

    file = models.FileField(
        upload_to="imports/",
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    user = models.ForeignKey(
        CustomUser,
        null=True,
        on_delete=models.SET_NULL,
    )

    detail = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )