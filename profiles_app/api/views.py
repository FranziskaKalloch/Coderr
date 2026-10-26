from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Profile
from .serializers import ProfileDetailSerializer, ProfileUpdateSerializer, BusinessUserSerializer, CustomerUserSerializer
from .permissions import IsOwner


class ProfileDetailView(APIView):
    ''' Provide access to individual user profiles for authenticated users '''
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ''' Retrieves a profile by the user ID provided in the URL.
        Returns the profile data or a 404 response if no matching profile exists '''

        profile = get_object_or_404(Profile, user_id=pk) # Wir suchen im Profile unter user_id (Profile.user_id = pk) Also nur die ID des Users wird mit dem pk verglichen
        serializer = ProfileDetailSerializer(profile) # Instanz erzeugt und dieser das Profil übergeben
        return Response(serializer.data)

    def patch(self, request, pk):
        ''' Partially updates a user profile after verifying that the requesting user owns it. '''
        profile = get_object_or_404(Profile, user_id=pk)
        self.permission_classes = [IsOwner]
        self.check_object_permissions(request, profile)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True) # partial=True -> wird verwendet, um eine REssource teilweise zu aktualisieren (Partial Update), das bedeutet der Client muss nicht alle Felder senden, sondern nur die, die geändert werden sollen
        if serializer.is_valid():
            serializer.save()
            serializer = ProfileDetailSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileBusinessUserView(APIView):
    ''' Returns a list of all business user '''
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = Profile.objects.filter(type="business")
        serializer = BusinessUserSerializer(profile, many=True)
        return Response(serializer.data)
        
    
class ProfileCustomerUserView(APIView):
    ''' Returns a list of all customer user ''' 
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = Profile.objects.filter(type="customer")
        serializer = CustomerUserSerializer(profile, many=True)
        return Response(serializer.data)  
