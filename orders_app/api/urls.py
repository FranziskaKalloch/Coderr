
from django.urls import path

from .views import OrderListCreateView, OrderCreateSerializer


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="orders"),
    path('orders/<int:id>', OrderCreateSerializer.as_view(), name="order-status")
]
