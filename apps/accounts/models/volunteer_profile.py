import uuid
from django.db import models
from django.core.validators import MinLengthValidator
from apps.core.models import BaseModel
from apps.core.constants import UserType, AvailabilityType
from .user import User
from .address import Address

class VolunteerProfile(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
        limit_choices_to={'user_type': UserType.VOLUNTEER}
    )

    bio = models.TextField(validators=[MinLengthValidator(100)], blank=True, null=True)
    availability = models.CharField(max_length=20, choices=AvailabilityType.CHOICES, default=AvailabilityType.FLEXIBLE)
    hours_per_week = models.PositiveIntegerField(default=5)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='volunteers')
    willing_to_travel = models.BooleanField(default=True)
    max_travel_distance_km = models.PositiveIntegerField(default=50)

    class Meta:
        db_table = 'volunteer_profiles'
        indexes = [
            models.Index(fields=['availability', 'willing_to_travel']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"