from rest_framework import serializers
from rest_framework.validators import ValidationError

from django.contrib.auth.models import User
from django.forms.models import __all__

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    '''  '''
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail")
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
 
 
class UserDetailSerializer(serializers.ModelSerializer):
    '''  '''
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class OfferSerializer(serializers.ModelSerializer):
    '''  '''
    details = OfferDetailSerializer(many=True, source="offer_details", read_only=True)
    user_details = UserDetailSerializer(read_only=True, source="user")
    min_price = serializers.FloatField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    class Meta:
        model = Offer
        fields = ('id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details')

class OfferDetailCreateSerializer(serializers.ModelSerializer):
    '''  '''
    features = serializers.ListField(child=serializers.CharField(max_length=100))
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES)
    class Meta:
        model = OfferDetail
        fields = ('id','title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type')
    
class OfferCreateSerializer(serializers.ModelSerializer):
    '''  '''
    details = OfferDetailCreateSerializer(many=True, min_length=3, max_length=3) # An Offer contains 3 Details!
    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
    
    def validate_details(self, data):
        ''' Check that each package type appears exactly once. '''
        offer_types = []  # Create an empty list to collect the package types.
        for detail in data: # Loop through the package dictionaries.
            each_type = detail['offer_type'] # Read the current package's type, such as "basic".
            offer_types.append(each_type)    # Add this type to the collection.
        
        unique_types = set(offer_types) # Convert the list to a set, which removes duplicate values
        
        if len(unique_types) != 3: # Reject the data if there are fewer than three distinct types.  # The field already requires exactly three packages.
            raise ValidationError('Die Pakettypen basic, standard und premium müssen jeweils einmal vorkommen.')
        
        return data
        
        
    def create(self, validated_data): # diese Methode wird aufgerufen, wenn ein Objekt erstellt werden soll
        ''' Create and return an offer object, given the validated data '''
        details = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        
        for detail in details:
            OfferDetail.objects.create(offer=offer,**detail)
        
        return offer

#### POST OFFERS
## Äußerer Serializer:
# title, image, description, details []

## Nested Serializer (details):
# eine Liste mit genau drei Paketen, Jedes Paket wird durch denselben Nested Serializer verarbeitet
# titles, revisions, delivery_time_in_days, price, features und offer_type

## features ist eine Liste von Strings
## offer_type eine Auswahl von drei Werten (basic, standard, premium)