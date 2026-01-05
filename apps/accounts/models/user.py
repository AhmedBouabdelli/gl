import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.constants import UserType

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    user_type = models.CharField(max_length=20, choices=UserType.CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    #last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    #login_count = models.PositiveIntegerField(default=0)
    # date_of_birth = models.DateField(blank=True, null=True)
    # Ratings moved to User model
    total_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    #last_rating_update = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['user_type', 'is_verified']),
            models.Index(fields=['total_rating']),
        ]

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    @property
    def average_rating(self):
        if self.rating_count == 0:
            return 0.0
        return self.total_rating

    @property
    def rating_display(self):
        if self.rating_count == 0:
            return "No ratings yet"
        return f"{self.average_rating:.1f} ⭐ ({self.rating_count} reviews)"