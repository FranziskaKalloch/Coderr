from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Profile 
from .serializers import ProfileDetailSerializer


class ProfileDetailView(APIView):
    ''' Provide access to individual user profiles for authenticated users '''
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        ''' Retrieves a profile by the user ID provided in the URL. 
        Returns the profile data or a 404 response if no matching profile exists '''
       
        profile = get_object_or_404(Profile, user_id=pk) # Wir suchen im Profile unter user_id (Profile.user_id = pk) Also nur die ID des Users wird mit dem pk verglichen
        serializer = ProfileDetailSerializer(profile) # Instanz erzeugt und dieser das Profil übergeben
        return Response(serializer.data)
    