from rest_framework import serializers

from ..models import Order

class RetrieveOrderSerializer(serializers.ModelSerializer):
    ''' Represent orders with customer, business user, package details, status, and timestamps. '''
    features = serializers.ListField(child=serializers.CharField(max_length=255))
    offer_type = serializers.ChoiceField(choices=Order.OFFER_TYPE_CHOICES)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    class Meta: 
        model = Order
        fields = ('id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at')
