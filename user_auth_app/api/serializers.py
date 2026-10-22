from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User

from profiles_app.models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    password = serializers.CharField(write_only=True, required=True)
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeated_password', 'type')
        
    def validate(self, data):
        '''  '''
        if data ['password'] != data ['repeated_password']:
            raise serializers.ValidationError("passwords must be the same")