from rest_framework import serializers

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
        
    # Hyperlinkedserializer 
 
 
 # class UserSerializer()
 
 
 
 # class OfferSerializer(serilizers.Modelserializer):   