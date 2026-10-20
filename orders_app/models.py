from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Order(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "basic"),
        ("standard", "standard"),
        ("premium", "premium")
    ]
    STATUS_CHOICES = [
        ("in_progress", "in_progress"),
        ("completed", "completed"),
        ("cancelled", "cancelled")
    ]
    
    customer_user = models.ForeignKey(User, related_name="customer_orders", on_delete=models.PROTECT)
    business_user = models.ForeignKey(User, related_name="business_orders", on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=200, choices=OFFER_TYPE_CHOICES)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
