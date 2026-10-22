from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from profiles_app.models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    """Validate registration data and create a user with an associated profile."""
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    password = serializers.CharField(write_only=True, required=True)
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeated_password', 'type')
        
    def validate(self, data):
        """Validate that passwords match and meet Django's password requirements."""
        if data ['password'] != data ['repeated_password']:
            raise serializers.ValidationError("passwords must be the same")
        
        user = User(
            username=data['username'],
            email=data['email'],
        )
        
        validate_password(data['password'], user)
        
        return data
    
    def create(self, validated_data):
        """Create a user with a hashed password and an associated profile."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        profile = Profile.objects.create(user=user, 
                                         type=validated_data['type'])
        return user 