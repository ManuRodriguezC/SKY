from django.views.generic import TemplateView
from apps.sky.utils import DashboardService

class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update(
            DashboardService.get_context()
        )
        user = self.request.user
        print("superuser:", user.is_superuser)
        print("staff:", user.is_staff)
        print("permiso directo:", user.user_permissions.filter(
            codename="add_customuser"
        ).exists())
        print("permiso por grupo:", user.groups.filter(
            permissions__codename="add_customuser"
        ).exists())
        print("permiso efectivo:", user.has_perm("accounts.add_customuser"))
        return context