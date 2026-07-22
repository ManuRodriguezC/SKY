from django.urls import path
from .views import (
    AutomationListView,
    AutomationCreateView,
    AutomationUpdateView,
    automationChangeStatus,
    automationDelete,
    execute_automation_now,
    test_automation,
)


urlpatterns = [
    path('automatizaciones/', AutomationListView.as_view(), name="automations"),
    path('registrar-automatizacion/', AutomationCreateView.as_view(), name="create_automation"),
    path('actualizar-automatizacion/<int:pk>/', AutomationUpdateView.as_view(), name="edit_automation"),
    path('cambiar-estado/<int:id>/', automationChangeStatus, name="change_status"),
    path('eliminar-automatizacion/<int:id>/', automationDelete, name="delete"),
    path('ejecutar-automatizacion/<int:id>/', execute_automation_now, name="execute_now"),
    path('test-automatizacion/<int:id>/', test_automation, name="test_automation")
]
