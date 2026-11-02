from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderListSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsCustomerForOrder, IsBusinessUserOfOrder
from ..models import Order
from offers_app.models import OfferDetail


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerForOrder]
    
    def get(self, request):
        ''' Return orders associated with the authenticated user as a customer or business user. '''
        orders = Order.objects.filter(Q(business_user=request.user) | Q(customer_user=request.user)) # finde alle Einträge die entweder customer oder business sind
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        ''' Create an order from an offer detail for the authenticated customer. '''
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

class OrderUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessUserOfOrder]
    
    def patch(self, request, id):
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)
        serializer = Order()
        # TODO 15: Pass the order instance and request.data to OrderStatusUpdateSerializer.
#          Use partial=True for the PATCH request.
# TODO 16: Validate the input with raise_exception=True.
# TODO 17: Save the updated order.
        output_serializer = OrderListSerializer(order)
# TODO 19: Return the complete order data with HTTP 200 OK.
