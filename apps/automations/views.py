from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.db.models import Q

from .forms import (
    AutomationForm,
    get_automation_filter_formset
)

from .models import Automation, AutomationLog, AutomationExecution
from apps.customers.utils import (
    get_type_customers,
    get_citys,
    get_gender,
    get_status_customers,
    get_nominas
)
from apps.automations.services.filter_engine import build_queryset
from apps.automations.tasks import execute_auto
from apps.automations.services.filter_engine import get_test_object
from apps.automations.services.send_service import send_customer_email
from apps.automations.utils import create_content


class AutomationListView(ListView):
    model = Automation
    template_name = "automation_list.html"
    context_object_name = "automations"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Automation.objects.exclude(deleted=True).order_by("id", "-active").exclude(deleted=True)
        
        status = self.request.GET.get("status")

        if status == "active":
            queryset = queryset.filter(active=True)
        elif status == "inactive":
            queryset = queryset.filter(active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        automations = Automation.objects.exclude(deleted=True).all()
        
        context.update({
            "actives": automations.filter(active=True).count(),
            "inactives": automations.filter(active=False).count(),
            "all": automations.count(),
            "logs": AutomationLog.objects.all().order_by("-id"),
        })
        
        return context
        
    
class AutomationCreateView(CreateView):

    model = Automation

    form_class = AutomationForm

    template_name = "automations/create.html"

    success_url = reverse_lazy(
        "automations"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.POST:

            context["filter_formset"] = (
                get_automation_filter_formset(1)(
                    self.request.POST,
                    self.request.FILES,
                    prefix="filters"
                )
            )

        else:

            context["filter_formset"] = (
                get_automation_filter_formset(1)(
                    prefix="filters"
                )
            )

        context.update({
            "title": "Nueva automatización",
            "type_customers": get_type_customers(),
            "citys": get_citys(),
            "genders": get_gender(),
            "status_customers": get_status_customers(),
            "nominas": get_nominas()
        })

        return context

    def form_valid(self, form):
        filter_formset = get_automation_filter_formset(1)

        filter_formset = filter_formset(
            self.request.POST,
            self.request.FILES,
            prefix="filters"
        )

        if not filter_formset.is_valid():

            return self.form_invalid(
                form
            )

        with transaction.atomic():
            self.object = form.save()

            filter_formset.instance = self.object

            filter_formset.save()

            AutomationLog.create_log(
                automation=self.object,
                action=AutomationLog.Action.CREATED,
                user=self.request.user,
            )

        return redirect(
            self.get_success_url()
        )


class AutomationUpdateView(UpdateView):

    model = Automation

    form_class = AutomationForm

    template_name = "automations/create.html"

    success_url = reverse_lazy(
        "automations"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.POST:

            context["filter_formset"] = (
                get_automation_filter_formset(0)(
                    self.request.POST,
                    self.request.FILES,
                    instance=self.object,
                    prefix="filters",
                )
            )

        else:

            context["filter_formset"] = (
                get_automation_filter_formset(0)(
                    instance=self.object,
                    prefix="filters",
                )
            )

        context.update({
            "title": "Actualizar automatización",
            "type_customers": get_type_customers(),
            "citys": get_citys(),
            "genders": get_gender(),
            "status_customers": get_status_customers(),
            "nominas": get_nominas(),
        })

        return context

    def form_valid(self, form):

        filter_formset = get_automation_filter_formset()(
            self.request.POST,
            self.request.FILES,
            instance=self.object,
            prefix="filters",
        )

        if not filter_formset.is_valid():

            return self.form_invalid(form)

        with transaction.atomic():

            changes = self._get_changes(
                automation=self.object,
                form=form,
                filter_formset=filter_formset,
            )

            self.object = form.save()

            filter_formset.instance = self.object

            filter_formset.save()

            if changes:

                AutomationLog.create_log(
                    automation=self.object,
                    action=AutomationLog.Action.UPDATED,
                    user=self.request.user,
                    detail="\n".join(changes),
                )

        return redirect(
            self.get_success_url()
        )
    
    def _get_changes(
        self,
        automation,
        form,
        filter_formset,
    ):

        changes = []

        # Cambios de la automatización
        for field in form.changed_data:

            model_field = automation._meta.get_field(
                field
            )

            changes.append(
                f"{model_field.verbose_name}: "
                f"'{getattr(automation, field)}' → "
                f"'{form.cleaned_data[field]}'"
            )

        # Cambios de los filtros
        for filter_form in filter_formset:

            # Filtro eliminado
            if (
                filter_form.is_valid()
                and filter_form.cleaned_data.get("DELETE")
            ):

                if filter_form.instance.pk:

                    changes.append(
                        f"Se eliminó el filtro: "
                        f"{filter_form.instance}"
                    )

                continue

            # Filtro nuevo
            if not filter_form.instance.pk:

                if filter_form.has_changed():

                    changes.append(
                        "Se agregó un nuevo filtro."
                    )

                continue

            # Filtro existente modificado
            for field in filter_form.changed_data:

                model_field = (
                    filter_form.instance
                    ._meta
                    .get_field(field)
                )

                old_value = getattr(
                    filter_form.instance,
                    field
                )

                new_value = filter_form.cleaned_data[
                    field
                ]

                changes.append(
                    f"{model_field.verbose_name}: "
                    f"'{old_value}' → '{new_value}'"
                )

        return changes


class ExecutionListView(ListView):
    model = AutomationExecution
    template_name = "automations/execution_list.html"
    context_object_name = "executions"
    
    paginate_by = 10
    
    def get_queryset(self):
        queryset = AutomationExecution.objects.all().order_by("-id")
        
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        
        if status == AutomationExecution.Status.SUCCESS:
            queryset = queryset.filter(status=AutomationExecution.Status.SUCCESS)
        elif status == AutomationExecution.Status.FAILED:
            queryset = queryset.filter(status=AutomationExecution.Status.FAILED)
        
        if search:
            queryset = queryset.filter(
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(customer__document__icontains=search) |
                Q(obligation__num_obligacion__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        executions = AutomationExecution.objects.all()
        
        context.update({
            "title_page": "Ejecuciones",
            "all": executions.count(),
            "success": executions.filter(status=AutomationExecution.Status.SUCCESS).count(),
            "failed": executions.filter(status=AutomationExecution.Status.FAILED).count(),
        })
        
        return context
    


def automationChangeStatus(request, id):
    automation = get_object_or_404(Automation, id=id)
    
    if not automation:
        messages.error(request, "Error al recuperar la automatizacion")
    
    automation.active = not automation.active

    if automation.active:
        message = "Se activo la automatizacion de forma correcta."
    else:
        message = "Se desactivo la automatizacion de forma correcta."

    automation.save()
    
    messages.success(request, message)
    status = AutomationLog.Action.ENABLED if automation.active else AutomationLog.Action.DISABLED
    AutomationLog.create_log(
        automation=automation,
        action=status,
        user=request.user,
    )
    
    return redirect('automations')

def automationDelete(request, id):
    automation = get_object_or_404(Automation, id=id)
    
    if not automation:
        messages.error(request, "Error al recuperar la automatizacion")
        
    if automation.active:
        messages.warning(
            request,
            "No es posible eliminar una automatización activa."
        )
        return redirect('automations')
    
    messages.success(
        request,
        "La automatización fue eliminada correctamente."
    )
    
    automation.deleted = True
    automation.save()
    
    AutomationLog.create_log(
        automation=automation,
        action=AutomationLog.Action.DELETED,
        user=request.user,
    )
    
    return redirect('automations')


def execute_automation_now(request, id):

    automation = get_object_or_404(Automation,id=id)

    try:
        executes = build_queryset(
            automation
        ).count()

        execute_auto.delay(automation.id)

        AutomationLog.create_log(
            automation=automation,
            action=AutomationLog.Action.EXECUTED,
            user=request.user,
            detail="Automatizacion ejecutada de forma manual."
        )
        messages.success(
            request,
            f"La automatización se ejecutará en segundo plano. Se procesarán {executes} contactos."
        )

    except Exception:

        messages.error(
            request,
            "Se presentó un error al enviar la automatización a la cola de ejecución."
        )

    return redirect("automations")

def test_automation(request, id):
    from apps.automations.services.email_connection import get_email_connection
    
    automation = get_object_or_404(Automation,id=id)
    
    try:
        object = get_test_object(automation)
        
        content = create_content(automation, object)
        
        connection = get_email_connection()
        
        send_customer_email(
            object=object,
            automation=automation,
            content=content,
            connection=connection
        )

        messages.success(
            request,
            f"La prueba de automatizacion se envio de forma exitosa, revise su correo origen o destino."
        )

    except Exception as e:
        print(e)