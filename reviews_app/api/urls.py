
from django.urls import path

from .views import ReviewView, ReviewUpdateDeleteView


urlpatterns = [
    path('reviews/', ReviewView.as_view(), name="reviews"),
    path('reviews/<int:id>/', ReviewUpdateDeleteView.as_view(), name="review-details")
]