from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AccountTests(APITestCase):
    def test_register(self):
        ''' Ensure we can create a new account '''
        url = reverse('registration')
        data = {
            "username": "Franziska",
            "email": "f.kalloch@outlook.de",
            "password": "TestPassword501",
            "repeated_password": "TestPassword501",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=data['username']).exists())
    
    def setUp(self):
        ''' Creates a dummy user in testing database '''
        self.username = "Solo"
        self.email = "HanSolo@outlook.de"
        self.password = "StarWars1999"
        self.user = User.objects.create_user(
            username = self.username,
            email = self.email,
            password = self.password
        )
        
        self.token = Token.objects.create(user=self.user)
        
        # URL für den Login Endpunkt
        self.login_url = reverse('login')
    
    def test_login(self):
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)