from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Profile

class ProfileTests(APITestCase):
    def setUp(self):
        ''' Create a test user and profile, and authenticate the test clien '''
        self.user = User.objects.create_user(username="Max_Mustermann", email="mustermann@web.de") # Testbenutzer erstellen
        self.profile = Profile.objects.create(user=self.user, type="customer", location="Berlin", description="Meine bisherige Beschreibung")# Zugehöriges Profil erstellen
        token = Token.objects.create(user=self.user) # Anmeldung vorbereiten
        self.url = reverse('profile-detail', args=[self.user.pk]) # URL vorbereiten
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}") # Token wird beim TestClient hinterlegt, damit dieser angemeldete Anfragen senden kann

    def test_get_profile(self):
        ''' Verify that an authenticated user can retrieve an existing profile '''
        response = self.client.get(self.url) # Anfrage senden
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Antwort prüfen
        self.assertEqual(response.data["username"], "Max_Mustermann")
        
    def test_get_profile_unauthenticated(self): # Profil existiert, Anmeldung fehlt
        ''' Verify that retrieving a profile without authentication returns HTTP 401 '''
        self.client.credentials() # Ohne Argumente entfernt sie die hinterlegten Zugangsdaten.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 
        
    def test_no_profile(self):
        ''' Verify that retrieving a non existent profile return HTTP 404 '''
        url = reverse('profile-detail', args=[500]) # eine ID, die in der Testdatenbank nicht existiert
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_edit_profile(self):
        '''  '''
        data = {
            "location": "Hamburg",
            "description": "Das ist die neue Beschreibung"
        }
        response = self.client.patch(self.url, data)
        self.profile.refresh_from_db() # lädt aktuell gespeicherte Werte aus der Datenbank in das Profilobjekt -> die neuen Werte liegen in self.profile.location und self.profile.description
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.location, "Hamburg") # prüft ob Hamburg tatsächlich in der db steht
        self.assertEqual(self.profile.description, "Das ist die neue Beschreibung")
    
    def test_edit_foreign_profile_forbidden(self): # Der Token aus dem setUp wird beibehalte. So versucht der erste Benutzer, das Profil des zweiten zu bearbeiten
        user = User.objects.create_user(
            username="Hans Wurst", email="wurst@web.de"
        )
        profile = Profile.objects.create(
            user=user, 
            type="customer", 
            location="München", 
            description="Das ist die Beschreibung von Hans Wurst"
        )
        
        data = {
            "location": "Essen"
        }
        
        url = reverse('profile-detail', args=[user.pk])
        response = self.client.patch(url, data)
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(profile.location, "München")
    
    def test_get_business_profiles(self):
        user = User.objects.create_user(
            username="Business_User", email="business@web.de"
        )
        profile = Profile.objects.create(
            user=user, type="business", location="Bonn", description="Ich bin Business User"
        )
        url = reverse('profile-business-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.type, 'business')
    
    def test_get_customer_profiles(self):
            url = reverse('profile-customer-list')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.profile.type, 'customer')
        
        
###### GET 
# einzelnes Profil 200 und richtige Profildaten; 
# 401 ohne Anmeldung; 
# 404 bei fehlendem Profil

##### PATCH 
# Profil 200 und Änderungen gespeichert; ausgelassene Felder bleiben erhalten; 
# 403 bei fremdem Profil; 

##### GET Business-Liste	
# 200 und ausschließlich Business-Profile; 

######GET Kunden-Liste	200 und ausschließlich Kundenprofile; 
# 401 ohne Anmeldung