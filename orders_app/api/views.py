from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from .serializers import OrderListSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer, OrderCountSerializer, CompletedOrderCountSerializer
from .permissions import IsCustomerForOrder, IsBusinessUserOfOrder
from ..models import Order
from offers_app.models import OfferDetail
from profiles_app import Profile


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
    def get_permissions(self):
        ''' Return permission instances based on the HTTP request method. '''
        if self.request.method == "DELETE":
            return (IsAuthenticated(), IsAdminUser())
        else:
            return (IsAuthenticated(), IsBusinessUserOfOrder())
    
    def patch(self, request, id):
        """Update an order's status after verifying that the authenticated user is the business user assigned to the order.
        Validate the request data and return the updated order."""
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        outcome_serializer = OrderListSerializer(order)
        return Response(outcome_serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        ''' Delete the specified order. Access is restricted to staff users. ''' 
        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id): 
        ''' Return the number of in-progress orders for the specified business user. '''
        get_object_or_404(Profile, user_id=business_user_id, type="business") # Django sucht in der Datenbank ein Profil, dessen Benutzer ID zur übergegebenen ID passt und dessen Typ business ist.
        order_count = Order.objects.filter(business_user_id=business_user_id, status="in_progress").count() # Django zählt die Bestellungen, die beide Bedingungen erfüllen, richtiger Business User und status. 
        serializer = OrderCountSerializer({"order_count": order_count}) # Bei einem Dictonary liest der Serializer den passenden Schlüssel aus. Bei einem Model-Objekt liest er das passendet Attribut
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        ''' Return the number of completed orders for specified business user '''
        get_object_or_404(Profile, user_id=business_user_id, type="business")
        completed_order_count = Order.objects.filter(business_user_id=business_user_id, status="completed").count()
        serializer = CompletedOrderCountSerializer({"completed_order_count": completed_order_count})
        return Response(serializer.data, status=status.HTTP_200_OK)