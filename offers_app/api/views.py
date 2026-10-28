from django.shortcuts import render
from django.db.models import Min

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from .serializers import OfferSerializer, OfferDetailSerializer, UserDetailSerializer
from ..models import Offer, OfferDetail

# 

class OfferListView(ListAPIView):
    """List offers with filtering, ordering, search and pagination."""
    permission_classes = [AllowAny]
    serializer_class = OfferSerializer
    
    filter_backends = [OrderingFilter, SearchFilter] # Um die Filter zu Aktivieren
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    
    
    

    
    
        
# Liste von Angeboten	Angebote aus der Datenbank abfragen
# Minimaler Preis und kürzeste Lieferzeit	Zwei Werte pro Angebot annotieren
# creator_id, min_price, max_delivery_time	Parameter prüfen und die Abfrage filtern
# search	Titel und Beschreibung durchsuchen
# ordering	Ergebnisse nach einem erlaubten Feld sortieren
# Paginierte Antwort	Mit PageNumberPagination eine Seite auswählen
# Angebotsdaten ausgeben	Diese Seite serialisieren und die Antwort zurückgeben
