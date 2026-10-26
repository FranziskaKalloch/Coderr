from django.urls import path
from .views import ProfileBusinessUserView, ProfileCustomerUserView, ProfileDetailView


urlpatterns = [
    path('profile/business/', ProfileBusinessUserView.as_view(), name="profile-business-list"),
    path('profile/customer/', ProfileCustomerUserView.as_view(), name="profile-customer-list"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="profile-detail")
]
