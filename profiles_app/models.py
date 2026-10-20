from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Profile(models.Model):
    
    TYPE_CHOICES = [
        ('customer', 'customer'), # first value = gespeicherter Wert | second value = angezeigte Bezeichnung
        ('business', 'business')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=16, validators=[RegexValidator(regex=r'^\+?[0-9]{9,15}\Z', message="Enter 9 to 15 digits, optionally starting with +, without spaces.")], blank=True) 
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file = models.ImageField(blank=True)
    uploaded_at = models.DateField(null=True, blank=True)