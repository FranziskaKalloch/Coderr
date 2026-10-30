from rest_framework import serializers
from rest_framework.validators import ValidationError

from django.contrib.auth.models import User
from django.forms.models import __all__
from django.db import transaction
from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    ''' Represent an offer package by its ID and detail URL. '''
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail")
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
 
 
class UserDetailSerializer(serializers.ModelSerializer):
    ''' Provide the offer creator's first name, last name, and username. '''
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class OfferSerializer(serializers.ModelSerializer):
    ''' Represent an offer with package links, creator information, minimum price, and shortest delivery time. '''
    details = OfferDetailSerializer(many=True, source="offer_details", read_only=True)
    user_details = UserDetailSerializer(read_only=True, source="user")
    min_price = serializers.FloatField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    class Meta:
        model = Offer
        fields = ('id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details')

class OfferDetailCreateSerializer(serializers.ModelSerializer):
    ''' Validate and represent an individual offer package, including its features and package type. '''
    features = serializers.ListField(child=serializers.CharField(max_length=100))
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES)
    class Meta:
        model = OfferDetail
        fields = ('id','title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type')
    
class OfferCreateSerializer(serializers.ModelSerializer):
    ''' Validate and create an offer with exactly three packages: basic, standard, and premium. '''
    details = OfferDetailCreateSerializer(many=True, min_length=3, max_length=3, source="offer_details") # An Offer contains 3 Details!
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
        
    @transaction.atomic  
    def create(self, validated_data): 
        ''' Create an offer and its associated packages in a single database transaction. '''
        details = validated_data.pop('offer_details')
        offer = Offer.objects.create(**validated_data)
        
        for detail in details:
            OfferDetail.objects.create(offer=offer,**detail)
        
        return offer
    
    class OfferRetrieveSerializer(OfferSerializer):
        ''' Serialize a single offer with detail links and metadata. '''
        class Meta(OfferSerializer.Meta):
            fields = ('id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time')
            
    class OfferUpdateSerializer(serializers.ModelSerializer):
        ''' Validate partial updates to an offer and its packages. '''
        details = OfferDetailCreateSerializer(many=True, source="offer_details")
        class Meta:
            model = Offer
            fields = ('id','title', 'image', 'description', 'details')
            
        @transaction.atomic   
        def update(self, instance, validated_data): # instance: the offer that should be updated, validated_data - 
            ''' Update the offer and any provided packages. '''
            # seperate detail fields from offer fields
            details = validated_data.pop('offer_details', None) 
            
            # update offer fields
            instance.title = validated_data.get("title", instance.title)
            instance.description = validated_data.get("description", instance.description)
            instance.image = validated_data.get("image", instance.image)
            instance.save()
            
            # update detail fields
            if details is not None:
                for detail_data in details:
                    offer_type = detail_data.get("offer_type")
                    
                    if offer_type is None:
                        raise serializers.ValidationError({
                            "details": "Für jedes Paket muss offer_type angegeben werden."
                        })
                    try:
                        detail_instance = instance.offer_details.get(offer_type=offer_type)
                    except OfferDetail.DoesNotExist:
                        raise serializers.ValidationError({
                            "details": f"Das Paket '{offer_type}' existiert nicht."
                        })
                    # update detail fields
                    detail_instance.title = detail_data.get("title", detail_instance.title)
                    detail_instance.revisions = detail_data.get("revisions", detail_instance.revisions)
                    detail_instance.delivery_time_in_days = detail_data.get("delivery_time_in_days", detail_instance.delivery_time_in_days)
                    detail_instance.price = detail_data.get("price", detail_instance.price)
                    detail_instance.features = detail_data.get("features", detail_instance.features)
                    detail_instance.save()

            return instance
            
