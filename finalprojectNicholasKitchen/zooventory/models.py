from django.db import models
from django.conf import settings

# --- Animal model ---
class Animal(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animals')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    age = models.PositiveIntegerField()  # CHECK (age >= 0) → PositiveIntegerField
    last_fed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.species})"


# --- Food model ---
class Food(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=100)
    amount = models.FloatField(null=True, blank=True)  # CHECK (amount >= 0)
    measurement = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.amount} {self.measurement}"