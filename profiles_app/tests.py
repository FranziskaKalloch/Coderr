from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Profile

class ProfileTests(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="Max_Mustermann", email="mustermann@web.de") # Testbenutzer erstellen
        profile = Profile.objects.create(user=user, type="customer")# Zugehöriges Profil erstellen
        token = Token.objects.create(user=user) # Anmeldung vorbereiten
        self.url = reverse('profile-detail', args=[user.pk]) # URL vorbereiten
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}") # Token wird beim TestClient hinterlegt, damit dieser angemeldete Anfragen senden kann

    def test_get_profile(self):
        response = self.client.get(self.url) # Anfrage senden
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Antwort prüfen
        self.assertEqual(response.data["username"], "Max_Mustermann")

# GET einzelnes Profil	200 und richtige Profildaten; 401 ohne Anmeldung; 404 bei fehlendem Profil
#PATCH Profil	200 und Änderungen gespeichert; ausgelassene Felder bleiben erhalten; 401 ohne Anmeldung; 403 bei fremdem Profil; 400 bei ungültigen Daten; 404 bei fehlendem Profil
#GET Business-Liste	200 und ausschließlich Business-Profile; 401 ohne Anmeldung
#GET Kunden-Liste	200 und ausschließlich Kundenprofile; 401 ohne Anmeldung