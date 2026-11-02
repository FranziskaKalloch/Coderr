from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderListSerializer, OrderCreateSerializer
from ..models import Order
from offers_app.models import OfferDetail


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(Q(business_user=request.user) | Q(customer_user=request.user)) # finde alle Einträge die entweder customer oder business sind
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data) # Eingabe Serializer: nimmt die gesendeten Daten entgegegen.
        serializer.is_valid(raise_exception=True) # prüft die Eingabe: ist die ID vorhanden...
        offer_detail_id = serializer.validated_data['offer_detail_id'] # holt die geprüfte ID aus den request Daten
        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id) # enthält nach der Suche, dass vollständige Model-Ojekt mit Preis, Titel etc
        return Response(serializer.validated_data) # sendet die geprüften Eingabe zurück, noch keine Ausgabe!

 