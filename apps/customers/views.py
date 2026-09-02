from django.contrib import messages
from django.db.models import Max
from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from pathlib import Path


from .models import Customer, ImportExecution
from .forms import ImportExcelForm
from .tasks import import_obligations


class CustomerListView(ListView):
    model = Customer
    template_name = "customers_list.html"
    context_object_name = "customers"

    paginate_by = 10

    def get_queryset(self):
        queryset = Customer.objects.exclude(test=True).order_by("-id")

        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
    
        if status == Customer.ACTIVE_PARAM:
            queryset = queryset.filter(
                status=Customer.ACTIVE
            )

        elif status == Customer.INACTIVE_PARAM:
            queryset = queryset.filter(
                status=Customer.INACTIVE
            )

        elif status == Customer.MORA_PARAM:
            queryset = queryset.filter(
                obligations__mora_days__gte=Customer.MORA_DAYS
            ).distinct()
            
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                document__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        customers = Customer.objects.exclude(test=True)

        context.update({
            "title_page": "Asociados",

            "num_customers": customers.count(),

            "actives": customers.filter(
                status=Customer.ACTIVE
            ).count(),

            "inactives": customers.filter(
                status=Customer.INACTIVE
            ).count(),

            "mora": customers.filter(
                obligations__mora_days__gte=Customer.MORA_DAYS
            ).distinct().count(),
        })

        return context
    

class CustomerDetail(DetailView):
    model = Customer
    template_name = "detail.html"
    context_object_name = "customer"

    def get_queryset(self):
        return (
            Customer.objects
            .prefetch_related("obligations", "logs")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obligations = (
            self.object.obligations
            .all()
            .order_by("-mora_days", "num_obligacion")
        )

        summary = {
            "total_obligations": obligations.count(),
            "max_mora": obligations.aggregate(
                Max("mora_days")
            )["mora_days__max"] or 0,
            "total_debt": sum(
                float(o.total)
                for o in obligations
                if o.total
            ),
        }

        context.update({
            "obligations": obligations,
            "logs": self.object.logs.order_by("-created_at"),
            "executions": self.object.executions.order_by("-id"),
            "summary": {
                "total_obligations": summary["total_obligations"] or 0,
                "max_mora": summary["max_mora"] or 0,
                "total_debt": summary["total_debt"] or 0,
                "obligations_in_mora": obligations.filter(
                    mora_days__gte=Customer.MORA_DAYS
                ).count(),
            },
        })

        return context


class ImportObligationsView(FormView):

    template_name = "import_obligations.html"

    form_class = ImportExcelForm

    success_url = reverse_lazy(
        "customers"
    )

    def form_valid(self, form):

        try:

            file = form.cleaned_data["file"]

            file_path = (
                Path("/app/files/log")
                / file.name
            )


            with open(file_path, "wb+") as destination:

                for chunk in file.chunks():
                    destination.write(chunk)
            
            import_obligations.delay(
                file.name
            )

            messages.success(
                self.request,
                "Se ha cargado de forma correcta."
            )

            return super().form_valid(form)

        except Exception as error:
            messages.error(
                self.request,
                "Se ha presentado un error al cargar el archivo."
            )

            return self.form_invalid(form)
        

# class ImportCustomersView(FormView):

#     template_name = "customers/import_customers.html"

#     form_class = ImportExcelForm

#     success_url = reverse_lazy(
#         "customers"
#     )

#     def form_valid(self, form):

#         execution = ImportExecution.objects.create(
#             file=form.cleaned_data["file"],
#             type=ImportExecution.Type.CUSTOMERS,
#             user=self.request.user,
#         )

#         import_customers.delay(
#             execution.id
#         )

#         messages.success(
#             self.request,
#             "El archivo fue cargado correctamente. "
#             "La importación se ejecutará en segundo plano.",
#         )

#         return redirect(
#             self.get_success_url()
#         )