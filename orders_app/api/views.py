from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderListSerializer, OrderCreateSerializer
from .permissions import IsCustomerForOrder
from ..models import Order
from offers_app.models import OfferDetail


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerForOrder]
    
    def get(self, request):
        orders = Order.objects.filter(Q(business_user=request.user) | Q(customer_user=request.user)) # finde alle Einträge die entweder customer oder business sind
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data) # Eingabe Serializer: nimmt die gesendeten Daten entgegegen.
        serializer.is_valid(raise_exception=True) # prüft die Eingabe: ist die ID vorhanden...
        offer_detail_id = serializer.validated_data['offer_detail_id'] # holt die geprüfte ID aus den request Daten
        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id) # enthält nach der Suche, dass vollständige Model-Ojekt mit Preis, Titel etc
        order = Order.objects.create( # die Bestellung wird erstellt und gespeichert
            customer_user=request.user, 
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            ) 
        output_serializer = OrderListSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED) # Gibt die erstellte Bestellung mit Status 201 zurück
