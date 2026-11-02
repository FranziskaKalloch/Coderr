
from django.urls import path

from .views import OrderListCreateView, OrderUpdateView


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="orders"),
    path('orders/<int:id>/', OrderUpdateView.as_view(), name="order-status")
]
