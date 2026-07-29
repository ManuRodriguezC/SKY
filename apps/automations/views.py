from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import (
    AutomationForm,
    AutomationFilterForm,
)

from .models import Automation, AutomationLog
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

            context["filter_form"] = (
                AutomationFilterForm(
                    self.request.POST,
                    self.request.FILES
                )
            )

        else:

            context["filter_form"] = (
                AutomationFilterForm()
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

        context = self.get_context_data()

        filter_form = context[
            "filter_form"
        ]

        if not filter_form.is_valid():

            return self.form_invalid(
                form
            )

        self.object = form.save()

        automation_filter = (
            filter_form.save(
                commit=False
            )
        )

        automation_filter.automation = (
            self.object
        )

        automation_filter.save()
        
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

        filter_instance = getattr(
            self.object,
            "filters_auto",
            None
        )

        if self.request.POST:
            context["filter_form"] = (
                AutomationFilterForm(
                    self.request.POST,
                    instance=filter_instance
                )
            )

        else:
            context["filter_form"] = (
                AutomationFilterForm(
                    instance=filter_instance
                )
            )
            

        context.update({
            "title": "Actualizar automatización",
            "type_customers": get_type_customers(),
            "citys": get_citys(),
            "genders": get_gender(),
            "status_customers": get_status_customers(),
            "nominas": get_nominas()
        })
        
        return context

    def form_valid(self, form):
        automation = self.get_object()

        context = self.get_context_data()

        filter_form = context["filter_form"]

        if not filter_form.is_valid():
            return self.form_invalid(form)

        automation_filter = getattr(
            automation,
            "filters_auto",
            None
        )

        changes = self._get_changes(
            automation=automation,
            automation_filter=automation_filter,
            form=form,
            filter_form=filter_form,
        )

        self.object = form.save()

        automation_filter = filter_form.save(
                commit=False
            )

        automation_filter.automation = (
            self.object
        )

        automation_filter.save()
        
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
        automation_filter,
        form,
        filter_form,
    ):
        changes = []

        for field in form.changed_data:
            model_field = automation._meta.get_field(field)

            changes.append(
                f"{model_field.verbose_name}: "
                f"'{getattr(automation, field)}' → "
                f"'{form.cleaned_data[field]}'"
            )

        if automation_filter:
            for field in filter_form.changed_data:
                model_field = automation_filter._meta.get_field(field)

                changes.append(
                    f"{model_field.verbose_name}: "
                    f"'{getattr(automation_filter, field)}' → "
                    f"'{filter_form.cleaned_data[field]}'"
                )

        return changes


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
    import traceback
    
    automation = get_object_or_404(Automation,id=id)
    
    try:
        object = get_test_object(automation)
        
        content = create_content(automation, object)
        
        send_customer_email(
            object=object,
            automation=automation,
            content=content,
        )

        messages.success(
            request,
            f"La prueba de automatizacion se envio de forma exitosa, revise su correo origen o destino."
        )

    except Exception as e:
        print(e)
        traceback.print_exc()
        messages.error(
            request,
            f"Se presentó un error al testear el correo de la automatizacion. {e}"
        )

    return redirect("automations")