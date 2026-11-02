from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import Offer, OfferDetail
from profiles_app.models import Profile
from django.contrib.auth.models import User
from django.urls import reverse


class OfferListCreateTest(APITestCase):
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
        ''' Test that the offers endpoint returns HTTP 200 OK. '''
        url = reverse("offers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_offer(self):
        ''' Test that a business user can create an offer successfully. '''
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
        
class OfferRetrieveUpdateDeleteTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Business_user2",
            email="business_user2@web.de", 
            password="IchBinBusinessUser2",  
        )
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.client.force_authenticate(user=self.user)
        
        self.offer = Offer.objects.create(
            user = self.user,
            title = "Retrieve, update and delete offer",
            description = "This is a test offer for test.py"
        )
    
    def test_get_offers(self):
        ''' Test that an offer can be retrieved by its ID. '''
        url = reverse('id-offer', kwargs={"id": self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer.id)
    
    def test_update_offer(self):
        ''' Test that an offer can be partially updated by its owner. '''
        url = reverse('id-offer', kwargs={"id": self.offer.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_offer(self):
        ''' Test that an offer can be deleted by its owner. '''
        url = reverse('id-offer', kwargs={"id": self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        
class OfferDetailTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Business_user2",
            email="business_user2@web.de", 
            password="IchBinBusinessUser2",  
        )
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.client.force_authenticate(user=self.user)
        
        self.offer = Offer.objects.create(
            user = self.user,
            title = "Retrieve, update and delete offer",
            description = "This is a test offer for test.py",
            )
            
        self.offerdetail = OfferDetail.objects.create(
            offer = self.offer,
            title = "Basic Desing",
            revisions = 2,
            delivery_time_in_days= 5,
            price = 100,
            features = ["Logo Design", "Visitenkarte"],
            offer_type = "basic"
        )
        
    def test_get_offerDetails(self):
        url = reverse("offer-detail", kwargs={"id": self.offerdetail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)