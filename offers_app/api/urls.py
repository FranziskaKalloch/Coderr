from django.urls import path, include
from .views import OfferListView, OfferDetailView, OfferRetrieveUpdateDeleteView

urlpatterns = [
    path('offers/', OfferListView.as_view() ,name="offers"),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name="offer-detail"),
    path('offers/<int:id>/', OfferRetrieveUpdateDeleteView.as_view(), name="id_offer"),
]
