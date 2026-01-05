import uuid
from django.db import models
from apps.core.models import BaseModel

class Address(BaseModel):
   
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    wilaya = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        db_table = 'addresses'
        indexes = [
            models.Index(fields=['wilaya', 'city']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f"{self.city}, {self.wilaya}, Algeria"