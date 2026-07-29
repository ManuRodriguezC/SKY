from calendar import monthrange
from datetime import date, timedelta

from django.db.models import Count, Q, Min
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.automations.models import (
    Automation,
    AutomationExecution,
)
from apps.customers.models import (
    Customer,
    Obligations,
)


class DashboardService:

    @classmethod
    def get_context(cls):

        return {
            "summary": cls.get_summary(),

            "current_month": cls.get_month_resume(
                cls.get_current_month()
            ),

            "previous_month": cls.get_month_resume(
                cls.get_previous_month()
            ),

            "automation_resume": cls.get_automation_resume(),

            "scheduled_automations": cls.get_scheduled_automations(),

            "today_automations": cls.get_today_automations(),

            "last_executions": cls.get_last_executions(),

            "customers_resume": cls.get_customers_resume(),

            "obligations_resume": cls.get_obligations_resume(),

            "cities_resume": cls.get_cities_resume(),

            "type_customer_resume": cls.get_type_customer_resume(),

            "execution_chart": cls.get_execution_chart(),

            "top_automations": cls.get_top_automations(),
        }

    ####################################################
    # Helpers
    ####################################################

    @classmethod
    def get_current_month(cls):
        today = timezone.localdate()
        return today.year, today.month

    @classmethod
    def get_previous_month(cls):

        today = timezone.localdate()

        if today.month == 1:
            return today.year - 1, 12

        return today.year, today.month - 1

    ####################################################
    # Resumen superior
    ####################################################

    @classmethod
    def get_summary(cls):
        
        six_month = timezone.now() - relativedelta(months=6)

        return {
            "customers": Customer.objects.exclude(test=True).count(),
            "obligations": Obligations.objects.exclude(customer__test=True).count(),
            "automations": Automation.objects.count(),
            "executions": AutomationExecution.objects.filter(
                executed_at__gte=six_month
            ).count(),
        }

    ####################################################
    # Mes
    ####################################################

    @classmethod
    def get_month_resume(
        cls,
        year_month,
    ):

        year, month = year_month

        qs = AutomationExecution.objects.filter(
            executed_at__year=year,
            executed_at__month=month,
        )

        return {

            "total": qs.count(),

            "success": qs.filter(
                status=AutomationExecution.Status.SUCCESS
            ).count(),

            "failed": qs.filter(
                status=AutomationExecution.Status.FAILED
            ).count(),
        }

    ####################################################
    # Automatizaciones
    ####################################################

    @classmethod
    def get_automation_resume(cls):

        return {

            "total": Automation.objects.exclude(deleted=True).count(),

            "active": Automation.objects.exclude(deleted=True).filter(
                active=True
            ).count(),

            "inactive": Automation.objects.exclude(deleted=True).filter(
                active=False
            ).count(),

        }

    ####################################################
    # Programadas
    ####################################################

    @classmethod
    def get_scheduled_automations(cls):

        return (
            Automation.objects.exclude(deleted=True).filter(
                active=True
            )
            .order_by(
                "hour",
                "name",
            )
        )

    ####################################################
    # Hoy
    ####################################################

    @classmethod
    def get_today_automations(cls):

        today = timezone.localdate()

        weekday = today.weekday()

        week = (today.day - 1) // 7

        return Automation.objects.filter(
            active=True,
            days_of_week__contains=[weekday],
            weeks_of_month__contains=[week],
        ).order_by(
            "hour"
        )

    ####################################################
    # Últimos envíos
    ####################################################

    @classmethod
    def get_last_executions(cls):

        return (
            AutomationExecution.objects
            .values(
                "automation",
                "automation__name",
                "executed_day",
            )
            .annotate(
                first_execution=Min("executed_at"),
                success=Count(
                    "id",
                    filter=Q(status=AutomationExecution.Status.SUCCESS)
                ),
                failed=Count(
                    "id",
                    filter=Q(status=AutomationExecution.Status.FAILED)
                ),
            )
            .order_by(
                "-first_execution"
            )[:10]
        )

    ####################################################
    # Asociados
    ####################################################

    @classmethod
    def get_customers_resume(cls):

        return {

            "total": Customer.objects.exclude(test=True).count(),

            "active": Customer.objects.exclude(test=True).filter(
                status=Customer.ACTIVE
            ).count(),

            "inactive": Customer.objects.exclude(test=True).filter(
                status=Customer.INACTIVE
            ).count(),

            "mora": Customer.objects.exclude(test=True).filter(
                obligations__mora_days__gt=Customer.MORA_DAYS
            ).distinct().count(),
        }

    ####################################################
    # Obligaciones
    ####################################################

    @classmethod
    def get_obligations_resume(cls):

        return {

            "total": Obligations.objects.exclude(customer__test=True).count(),

            "mora": Obligations.objects.exclude(customer__test=True).filter(
                mora_days__gt=Customer.MORA_DAYS
            ).count(),

            "current": Obligations.objects.exclude(customer__test=True).filter(
                mora_days__lte=Customer.MORA_DAYS
            ).count(),
        }

    ####################################################
    # Ciudades
    ####################################################

    @classmethod
    def get_cities_resume(cls):

        return (

            Customer.objects
            .exclude(test=True)
            .values(
                "city"
            )
            .annotate(
                total=Count("id")
            )
            .order_by(
                "-total"
            )[:10]
        )

    ####################################################
    # Tipo asociado
    ####################################################

    @classmethod
    def get_type_customer_resume(cls):

        return (

            Customer.objects
            .exclude(test=True)
            .values(
                "type_customer"
            )
            .annotate(
                total=Count("id")
            )
            .order_by(
                "-total"
            )
        )

    ####################################################
    # Grafica mensual
    ####################################################

    @classmethod
    def get_execution_chart(cls):

        today = timezone.localdate()

        days = monthrange(
            today.year,
            today.month,
        )[1]

        result = []

        for day in range(
            1,
            days + 1,
        ):

            total = AutomationExecution.objects.filter(

                executed_day=date(
                    today.year,
                    today.month,
                    day,
                )

            ).count()

            result.append({

                "day": day,

                "total": total,

            })

        return result

    ####################################################
    # Top automatizaciones
    ####################################################

    @classmethod
    def get_top_automations(cls):

        return (

            AutomationExecution.objects

            .values(
                "automation__name"
            )

            .annotate(

                total=Count("id")

            )

            .order_by(
                "-total"
            )[:5]

        )