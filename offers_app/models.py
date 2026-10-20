from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100, blank=False, null=False)
    image = models.ImageField(blank=True)
    description = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # offer_type ?
    # details = models.?
    

# Jedes OfferDetail gehört genau zu einem Angebot!
class OfferDetail(models.Model):
    
    OFFER_TYPE_CHOICES = [
        ("basic", "basic"),
        ("standard", "standard"),
        ("premium", "premium")
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title =models.CharField(max_length=200, blank=False)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=15, choices=OFFER_TYPE_CHOICES)