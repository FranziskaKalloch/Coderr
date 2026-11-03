from django.shortcuts import render
from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer
from .serializers import BaseInfoSerializer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return public platform statistics, including review counts, average rating, business profiles, and offers."""
        review_count = Review.objects.count()
        
        average_rating = Review.objects.aggregate(Avg("rating")) # Hier wird der Durchschnitt berechnet. Das Ergebnis ist ein Dictonary. {"rating__avg": 4.333333333333333}. Den Schlüssel rating__avg erzeugt Django aus dem Feldnamen rating und der Berechnung avg.
        average_rating = average_rating["rating__avg"] # hier wird die Zahl aus dem Dictonary geholt. Davor war es ein Dict, jetzt ist es nur noch eine Zahl
        
        if average_rating is None:
            average_rating = 0.0
        
        average_rating = round(average_rating, 1)
        
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()
        
        serializer = BaseInfoSerializer({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        })
        return Response(serializer.data, status=status.HTTP_200_OK)