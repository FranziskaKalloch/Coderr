from django.shortcuts import render
from django.db.models import Min

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import OfferSerializer, OfferDetailSerializer, UserDetailSerializer
from ..models import Offer, OfferDetail

# 

class OfferListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Ausgangsabfrage inklusive der berechneten Werte (Annotate)
        offers = Offer.objects.annotate(
            min_price=Min("offer_details__price"), 
            min_delivery_time=Min("offer_details__delivery_time_in_days")) 
        
        # Query Parameter abfangen
        creator_id = request.query_params.get("creator_id")
        
        # Wenn übergeben, das bereits annotierte Queryset filtern
        if creator_id is not None:
           offers = offers.filter(user_id=creator_id)
        
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)
        
        
# Liste von Angeboten	Angebote aus der Datenbank abfragen
# Minimaler Preis und kürzeste Lieferzeit	Zwei Werte pro Angebot annotieren
# creator_id, min_price, max_delivery_time	Parameter prüfen und die Abfrage filtern
# search	Titel und Beschreibung durchsuchen
# ordering	Ergebnisse nach einem erlaubten Feld sortieren
# Paginierte Antwort	Mit PageNumberPagination eine Seite auswählen
# Angebotsdaten ausgeben	Diese Seite serialisieren und die Antwort zurückgeben
