
from django.urls import path

from .views import OrderListCreateView


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="orders"),
]


# TODO 20: Import OrderUpdateView.
# TODO 21: Connect orders/<int:id>/ to OrderUpdateView.as_view().
# TODO 22: Give the route a name, for example order-detail.