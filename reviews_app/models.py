from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Review(models.Model):
    business_user = models.ForeignKey(User, related_name="business_user_review", on_delete=models.CASCADE) # wer wird bewertet
    reviewer = models.ForeignKey(User, related_name="reviewer", on_delete=models.CASCADE) # Wer schreibt die Bewertung
    rating = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)