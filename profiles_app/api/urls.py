from django.urls import path
from .views import BusinessProfileListView, CustomerProfileListView, ProfileDetailView


urlpatterns = [
    path('profile/business/', BusinessProfileListView.as_view(), name="profile-business-list"),
    path('profile/customer/', CustomerProfileListView.as_view(), name="profile-customer-list"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="profile-detail")
]
