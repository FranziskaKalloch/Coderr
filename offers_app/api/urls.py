from django.urls import path, include
from .views import OfferListView, OfferDetailView

urlpatterns = [
    path('offers/', OfferListView.as_view() ,name="offers"),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name="offer-detail")
]
