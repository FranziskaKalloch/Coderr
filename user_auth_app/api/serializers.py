from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
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
        Token.objects.create(user=user) # create Token in Serializer
        return user 
    
class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField()
        
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password']) # prüft die Zugangsdaten
        
        if user is None: # wenn kein user gefunden wurde
          raise serializers.ValidationError('Username and password are invalid')
       
        data['user'] = user # bei Erfolg wird der Benutzer in data gespeichert
        return data 
       
       
       
       