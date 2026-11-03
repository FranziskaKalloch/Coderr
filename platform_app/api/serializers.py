from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    '''Represent platform statistics, including review count, average rating, business profile count, and offer count.'''
    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()