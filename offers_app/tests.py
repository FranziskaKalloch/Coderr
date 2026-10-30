from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import Offer, OfferDetail
from profiles_app.models import Profile
from django.contrib.auth.models import User
from django.urls import reverse




class OfferListCreateTest(APITestCase):
    ''' '''
    def setUp(self):
        ''' Create a test business user  '''
        self.business_user = User.objects.create_user(
            username="Business_user", 
            email="business@web.de", 
            password="IchBinBusinessUser",
            )
        self.profile = Profile.objects.create(user=self.business_user, type="business")
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        
    def test_get_offers(self):
        url = reverse("offers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_offer(self):
        url = reverse("offers")
        data = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 10,
                    "price": 50,
                    "features": ["Logo"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": 100,
                    "features": ["Logo", "Visitenkarte"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": 5,
                    "delivery_time_in_days": 5,
                    "price": 150,
                    "features": ["Logo", "Visitenkarte", "Briefpapier"],
                    "offer_type": "premium"
                }
                ]
            }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)