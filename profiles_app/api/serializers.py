from rest_framework import serializers

from ..models import Profile


class ProfileDetailSerializer(serializers.ModelSerializer):
    ''' Serializes profile details, including related user information, for API responses. '''
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True) 
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    created_at = serializers.DateTimeField(source="user.date_joined", read_only=True)
    
    class Meta:
        model = Profile
        fields = ('user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at') 

class ProfileUpdateSerializer(serializers.ModelSerializer):
    ''' Validates and updates editable profile fields and related user information. '''
    first_name = serializers.CharField(source="user.first_name", allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", allow_blank=True)
    email = serializers.EmailField(source="user.email")
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name','location', 'tel', 'description', 'working_hours', 'email') # nur die Felder, die bearbeitet werden dürfen!

    def update(self, instance, validated_data): # self: die Serializer Instance, instance: das bestehende Profil, validated_data: die bereits gerpüften Daten
        ''' '''
        user_data = validated_data.pop('user', {}) # User-Daten aus den validated_data entnehmen und in user_data speichern
        # User aktualisieren
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.email = user_data.get('email', instance.user.email)
        
        instance.user.save()
        
        # Profil aktualisieren
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        
        instance.save()
        
        return instance