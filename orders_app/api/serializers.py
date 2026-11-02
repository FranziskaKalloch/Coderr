from rest_framework import serializers

from ..models import Order

class OrderListSerializer(serializers.ModelSerializer):
    ''' Represent orders with customer, business user, package details, status, and timestamps. '''
    features = serializers.ListField(child=serializers.CharField(max_length=255))
    offer_type = serializers.ChoiceField(choices=Order.OFFER_TYPE_CHOICES)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    class Meta: 
        model = Order
        fields = ('id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    ''' Validate the offer detail ID provided to create an order. '''
    offer_detail_id = serializers.IntegerField(min_value=1)
    

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    ''' Validate and update the status of an order. '''
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    class Meta:
        model = Order
        fields = ('status',)

# TODO 3: Configure Meta to use Order and expose only the status field.
# TODO 4: Use Order.STATUS_CHOICES to validate the status.
#         ModelSerializer derives these choices from the model automatically.
# TODO 5: Reject any submitted field other than status with a ValidationError.
#         Listing only status in Meta.fields does not reject unknown input fields.