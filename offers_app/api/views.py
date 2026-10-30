from django.shortcuts import render
from django.db.models import Min
from django.shortcuts import get_object_or_404

from decimal import Decimal, InvalidOperation

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .serializers import OfferSerializer, OfferDetailSerializer, UserDetailSerializer, OfferCreateSerializer, OfferRetrieveSerializer
from .permissions import BusinessUser
from ..models import Offer, OfferDetail
from .pagination import OfferPagination

class OfferListView(ListAPIView):
    """List offers with filtering, ordering, search and pagination."""
    permission_classes = [AllowAny, BusinessUser]
    serializer_class = OfferSerializer
    pagination_class = OfferPagination
    
    filter_backends = [OrderingFilter, SearchFilter] # Um die Filter zu Aktivieren
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    
    def get_queryset(self):
        ''' Annotate offers with their minimum price and shortest delivery time, then filter by creator, minimum price, and maximum delivery time. '''
        queryset = Offer.objects.annotate(
                min_price=Min("offer_details__price"),
                min_delivery_time=Min("offer_details__delivery_time_in_days"), 
            )
        creator_id = self.request.query_params.get("creator_id")
        
        if creator_id is not None:
            try:
                creator_id = int(creator_id)
            except ValueError:
                raise ValidationError({"creator_id": "Fehlermeldung"})
            queryset = queryset.filter(user=creator_id)
    
        price_limit = self.request.query_params.get("min_price")
        
        if price_limit is not None:
            try:
                price_limit = Decimal(price_limit)
                if not price_limit.is_finite():
                    raise InvalidOperation
                
            except InvalidOperation:
                raise ValidationError({
                    "min_price": "Bitte gebe eine gültige Zahl an"
                })
                
            queryset = queryset.filter(min_price__gte=price_limit)
            
        delivery_limit = self.request.query_params.get("max_delivery_time")
        
        if delivery_limit is not None:
            try:
                delivery_limit = int(delivery_limit)
            except ValueError:
                raise ValidationError({
                    "max_delivery_time": "Bitte gib eine ganze Zahl an"
                })
            queryset = queryset.filter(min_delivery_time__lte=delivery_limit)
        
        return queryset
    
    def post(self, request):
        ''' Validate the request data and create an offer for the authenticated user. '''
        serializer = OfferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
class OfferDetailView(RetrieveAPIView):
    ''' Retrieve an offer package by its ID with public access. '''
    permission_classes = [AllowAny]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer


class OfferRetrieveUpdateDeleteView(APIView):
    ''' Endpoint to retrieve, update and delete objects by id '''
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        ''' retrieve a single offer by its ID '''
        queryset = Offer.objects.annotate(
            min_price=Min("offer_details__price"),
            min_delivery_time=Min("offer_details__delivery_time_in_days")
        )
        
        offer = get_object_or_404(queryset, id=id)
        serializer = OfferRetrieveSerializer(offer,
                                             context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        ''' updated partial fields of a single offer by its ID '''
        pass
    
    def delete(sel, request, id):
        '''  '''
        pass