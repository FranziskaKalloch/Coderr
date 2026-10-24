from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data) # nimmt die vom User eingegebenen Daten an
        serializer.is_valid(raise_exception=True) # stößt die Validierung im Serializer an
        user = serializer.save() # weil hier kein bestehendes Objekt übergeben wurde, ruft save() die create Methode auf, mit den validierten Daten(validated_data)
        token = Token.objects.get(user=user) # get token that was created in serializer
        return Response({"token": token.key, 
                         "username": user.username, 
                         "email": user.email, 
                         "user_id": user.id}, 
                        status=status.HTTP_201_CREATED)
        
# Die View ruft serializer.save() auf.
# Dadurch läuft create() im Serializer: User, Profil und Token werden gespeichert.
# create() gibt nur den User zurück. Dieser landet in der Variable user der View.
# Mit Token.objects.get(user=user) liest die View den zugehörigen Token aus der Datenbank.
# token.key liefert den eigentlichen Token-String für die Antwort.

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token=Token.objects.get(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)
        