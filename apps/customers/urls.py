from django.urls import path
from .views import (
  CustomerListView,
  CustomerDetail,
  ImportObligationsView
)


urlpatterns = [
    path('asociados/', CustomerListView.as_view(), name="customers"),
    path("asociados/<int:pk>/", CustomerDetail.as_view(),name="customer_detail",),
    path(
        "importar-obligaciones/",
        ImportObligationsView.as_view(),
        name="import_obligations",
    ),
]
