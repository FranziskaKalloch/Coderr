from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .serializers import ReviewSerializer, ReviewCreateSerializer
from ..models import Review
from orders_app.api.permissions import IsCustomerForOrder
class ReviewView(APIView):
    def get_permissions(self):
        ''' Return permission instances based on the HTTP request method. '''
        if self.request.method == "GET":
            return (IsAuthenticated(),)
        if self.request.method == "POST":
            return (IsAuthenticated(), IsCustomerForOrder())
        return (IsAuthenticated(),)
    
    def get(self, request):
        ''' Return all reviews with optional filtering by business user and reviewer and ordering by update time or rating. '''
        queryset = Review.objects.all()    
        business_user_id = request.query_params.get("business_user_id")
        
        if business_user_id is not None:
            try:
                business_user_id = int(business_user_id)
            except ValueError:
                raise ValidationError({"business_user_id": "Bitte eine gültige Zahl eingeben"})
        
        reviewer_id = request.query_params.get("reviewer_id")
        
        if reviewer_id is not None:
            try:
                reviewer_id = int(reviewer_id)
            except ValueError:
                raise ValidationError({"reviewer_id": "Bitte eine gültige ganze Zahl angeben."})
        
        ordering = request.query_params.get("ordering")
        
        if business_user_id is not None:
            queryset = queryset.filter(business_user_id = business_user_id)
        
        if reviewer_id is not None:
            queryset = queryset.filter(reviewer_id = reviewer_id)
        
        if ordering in ("updated_at", "rating"):
            queryset = queryset.order_by(ordering)
            
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        ''' Validate and create a review by the authenticated customer and return its details. '''
        serializer = ReviewCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save(reviewer=request.user)
        outcome_serializer = ReviewSerializer(review)
        return Response(outcome_serializer.data, status=status.HTTP_201_CREATED)
   