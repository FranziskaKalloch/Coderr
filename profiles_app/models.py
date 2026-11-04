from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    
    TYPE_CHOICES = [
        ('customer', 'customer'), # first value = gespeicherter Wert | second value = angezeigte Bezeichnung
        ('business', 'business')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=30, blank=True) 
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file = models.ImageField(blank=True)
    uploaded_at = models.DateField(null=True, blank=True)