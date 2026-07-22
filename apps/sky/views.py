from django.views.generic import TemplateView
from apps.sky.utils import DashboardService

class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update(
            DashboardService.get_context()
        )

        return context