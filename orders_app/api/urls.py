
from django.urls import path

from .views import OrderListCreateView, OrderUpdateView, OrderCountView, CompletedOrderCountView


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="orders"),
    path('orders/<int:id>/', OrderUpdateView.as_view(), name="order-status"),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name="order-count"),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name="completed-order-count"),
]
