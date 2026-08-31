from django.db import models

from apps.customers.models import Customer, Obligations
from apps.accounts.models import CustomUser

ALLOWED_FILTERS = {
    "mora_days",
    "age",
    "gender",
    "city",
    "score",
    "status",
    "nomina_name",
    "type_customer",
    "credit_line",
}

OPERATORS = {
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "between",
    "contains",
    "in",
}

LIST_WEEKS = {
    0: "1",
    1: "2",
    2: "3",
    3: "4",
    4: "5",
}

LIST_DAYS = {
    0: "Lunes",
    1: "Martes",
    2: "Miercoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sabado",
    6: "Domingo"
}

LIST_HOUR = {
    8: "08:00 AM",
    9: "09:00 AM",
    10: "10:00 AM",
    11: "11:00 AM",
    12: "12:00 PM",
    13: "01:00 PM",
    14: "02:00 PM",
    15: "03:00 PM",
    16: "04:00 PM",
    17: "05:00 PM",
}


class AutomationAction(models.TextChoices):

    SEND_EMAIL = (
        "send_email",
        "Enviar correo"
    )


class AutomationHour(models.IntegerChoices):
    H08 = 8, "08:00 AM"
    H09 = 9, "09:00 AM"
    H10 = 10, "10:00 AM"
    H11 = 11, "11:00 AM"
    H12 = 12, "12:00 PM"
    H13 = 13, "01:00 PM"
    H14 = 14, "02:00 PM"
    H15 = 15, "03:00 PM"
    H16 = 16, "04:00 PM"
    H17 = 17, "05:00 PM"

class EmailFormat(models.TextChoices):

    HTML = (
        "html",
        "HTML"
    )

    TEXT = (
        "text",
        "Texto plano"
    )

class Automation(models.Model):
    name = models.CharField(max_length=100)
    
    description = models.TextField(
        blank=True
    )
    
    active = models.BooleanField(default=True)
    
    hour = models.IntegerField(
        choices=AutomationHour.choices
    )
    
    date_from = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha inicio",
    )
    
    date_to = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin",
    )
    
    days_of_week = models.JSONField(default=list)
    
    weeks_of_month = models.JSONField(default=list)
    
    action = models.CharField(
        max_length=50,
        choices=AutomationAction.choices
    )
    
    content_type = models.CharField(
        max_length=10,
        choices=EmailFormat.choices,
        default=EmailFormat.HTML,
    )
    
    subject = models.CharField(
        max_length=255,
        blank=True
    )

    body = models.TextField()
    
    image = models.ImageField(
        upload_to="automations/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    deleted = models.BooleanField(
        default=False,
    )
    
    
    def __str__(self):
        return self.name
    
    def list_days(self):
        days = [LIST_DAYS[day] for day in self.days_of_week]
        if len(days) > 0:
            return "Dias: " + ", ".join(days)
        return "No tiene dias definidos"

    def list_weeks(self):
        weeks = [LIST_WEEKS[week] for week in self.weeks_of_month]
        if len(weeks) > 0:
            return "Semana " + ", ".join(weeks)
        return "No tiene semanas definidas"
    
    def get_hour(self):
        return LIST_HOUR[self.hour]
    
    def get_status(self):
        if self.active:
            return "Activa"
        return "Inactiva"
    
    def range_date(self):
        if self.date_from and self.date_to:
            return f"{self.date_from} / {self.date_to}"
        return "No definido"
    
    @property
    def apply(self):
        from apps.automations.services.filter_engine import build_queryset
        return build_queryset(self).count()


class AutomationLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Creada"
        UPDATED = "updated", "Actualizada"
        ENABLED = "enabled", "Activada"
        DISABLED = "disabled", "Desactivada"
        EXECUTED = "executed", "Ejecutada"
        DELETED = "deleted", "Eliminada"
    
    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="log"
    )
    
    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )
    
    user = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    
    created = models.DateTimeField(auto_now_add=True)
    
    detail = models.TextField(blank=True, default="")
    
    @classmethod
    def create_log(cls, automation, action, user=None, detail=""):
        return cls.objects.create(
            automation=automation,
            action=action,
            user=user,
            detail=detail,
        )


class FilterField(models.TextChoices):

    MORA_DAYS = (
        "mora_days",
        "Días Mora"
    )

    AGE = (
        "age",
        "Edad"
    )

    GENDER = (
        "gender",
        "Género"
    )

    CITY = (
        "city",
        "Ciudad"
    )

        # SCORE = (
        #     "score",
        #     "Score"
        # )
    
    STATUS = (
        "status",
        "Estado del asociado"
    )
    
    TYPE_ASSOCIATE = (
        "type_associate",
        "Tipo de asociado"
    )
    
    NOMINAS = (
        "nomina_name",
        "Nominas"
    )


class FilterOperator(models.TextChoices):

    EQ = "eq", "Igual"

    GTE = "gte", "Mayor o igual"

    LT = "lt", "Menor"

    LTE = "lte", "Menor o igual"

    BETWEEN = "between", "Entre"

    IN = "in", "En lista"
    
    DIF = "diff", "Diferente"


class AutomationFilter(models.Model):

    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="filters"
    )

    field = models.CharField(
        max_length=50,
        choices=FilterField.choices
    )

    operator = models.CharField(
        max_length=20,
        choices=FilterOperator.choices
    )

    value = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    range_from = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    range_to = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )


class AutomationExecution(models.Model):
    
    class Status(models.TextChoices):
        SUCCESS = (
            "success",
            "Enviado"
        )
        FAILED = (
            "failed",
            "Fallido"
        )

    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="executions"
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="executions"
    )
    
    obligation = models.ForeignKey(
        Obligations,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executions",
    )
    
    email = models.EmailField()
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices
    )
    
    message = models.TextField(max_length=1000)
    
    executed_at = models.DateTimeField(
        auto_now_add=True
    )

    executed_day = models.DateField(
        auto_now_add=True
    )

    def get_status(self):
        if self.status == self.Status.SUCCESS:
            return "Exitoso"
        return "Fallido"
    
    @classmethod
    def register_success(
        cls,
        automation,
        object,
        message
    ):
        if isinstance(object, Customer):    
            cls.objects.create(
                automation=automation,
                customer=object,
                email=object.email,
                status=cls.Status.SUCCESS,
                message=message,
            )
        
        if isinstance(object, Obligations):
            cls.objects.create(
                automation=automation,
                customer=object.customer,
                obligation=object,
                email=object.customer.email,
                status=cls.Status.SUCCESS,
                message=message,
            )


    @classmethod
    def register_failed(
        cls,
        automation,
        object,
        message,
    ):

        try:
            if isinstance(object, Customer):
                cls.objects.create(
                    automation=automation,
                    customer=object,
                    email=object.email or "",
                    status=cls.Status.FAILED,
                    message=message,
                )

            elif isinstance(object, Obligations):
                cls.objects.create(
                    automation=automation,
                    customer=object.customer,
                    obligation=object,
                    email=getattr(object.customer, "email", "") or "",
                    status=cls.Status.FAILED,
                    message=message,
                )

        except Exception as e:
            print(f"Error registrando la ejecución fallida de la automatización {e}")

