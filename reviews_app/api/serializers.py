from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    ''' Represent a review with its ID, business user, reviewer, rating, description, and timestamps. '''
    class Meta:
        model = Review
        fields = ('id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at')

class ReviewCreateSerializer(serializers.ModelSerializer):
    ''' Validate the business user, rating, and description provided to create a review. '''
    class Meta:
        model = Review
        fields = ('business_user', 'rating', 'description')
    
    def validate_business_user(self, value): # value ist das User Objekt
        """Ensure that the selected user has a business profile."""
        profile = getattr(value, "profile", None)
        
        if profile is None or profile.type != "business":
            raise serializers.ValidationError("Der ausgewählte Benutzer muss ein Business-Profil besitzen")
        
        return value
    
    def validate(self, validated_data):
        ''' Prevent customers from reviewing the same business user more than once.'''
        business_user = validated_data["business_user"]
        reviewer = self.context["request"].user # wird aus der Anfrage gelesen
        
        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists(): # sucht die gespeicherten Bewertungen, beschränkt sie auf Customer
            raise serializers.ValidationError("Du hast diesen Business-Benutzer bereits bewertet")
        
        return validated_data
        
        