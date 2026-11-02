from django.shortcuts import render
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderListSerializer
from ..models import Order


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(Q(business_user=request.user) | Q(customer_user=request.user)) # finde alle Einträge die entweder customer oder business sind
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
    
    def post(self, request):
        pass