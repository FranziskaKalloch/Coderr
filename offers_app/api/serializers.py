from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
 
 
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')
 
 
 
# class OfferSerializer(serilizers.Modelserializer):   