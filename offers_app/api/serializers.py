from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail")
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
 
 
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, source="offer_details", read_only=True)
    user_details = UserDetailSerializer(read_only=True, source="user")
    min_price = serializers.FloatField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    class Meta:
        model = Offer
        fields = ('id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details')