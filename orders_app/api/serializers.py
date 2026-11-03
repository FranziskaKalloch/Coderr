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
        
    def validate(self, data): # Methode wird aufgerufen während is_valid() läuft. Data enthält bereits die geprüften Felder. Sie macht zwei Dinge: lehnt Felder ab, die nicht status sind, und stellt sicher, das status überhaupt mitgeschickt wurde
        """Reject fields other than 'status' and require 'status' to be provided, including during partial updates. Return the validated data."""
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                f"Unzulässige Felder: {' ,' .join(sorted(unknown))}"
            )
        if "status" not in data:
            raise serializers.ValidationError({"status": "Dieses Feld ist erforderlich"})
        return data

# set() ist eine Menge, also eine Sammlung ohne Reihenfolge und ohne Duplikate. Bei einem Dict liefert set() die Schlüssel. 
# Das Minus zwischen set() bedeutet Differenz, alles was in a ist, aber nicht in b
# set(geschickte Daten) - set(erlaubte Daten)
# sorted() sortiert die Sammlung und gibt eine Liste zurück
# join() das klebt eine Liste von Texten mit einem Trennzeichen zusammen
# self.initial_data = wenn der Serializer in der View erzeugt wird, dann speichert DRF bei data= was übergeben wird, self.initial_data sind die Rohdaten aus dem REquest, 
# self.fields = 

class OrderCountSerializer(serializers.Serializer):
    ''' Represent the number of in-progress orders for a business user '''
    order_count = serializers.IntegerField()
    
class CompletedOrderCountSerializer(serializers.Serializer):
    ''' Represent the number of completed orders for a business user '''
    completed_order_count = serializers.IntegerField()