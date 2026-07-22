from django.urls import path
from .views import (
  CustomerListView,
  CustomerDetail
)


urlpatterns = [
    path('asociados/', CustomerListView.as_view(), name="customers"),
    path("asociados/<int:pk>/", CustomerDetail.as_view(),name="customer_detail",),
]
