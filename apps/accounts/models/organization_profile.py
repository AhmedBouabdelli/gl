import uuid
from django.db import models
from django.core.validators import MinLengthValidator
from apps.core.models import BaseModel
from apps.core.constants import UserType, OrganizationType
from .user import User
from .address import Address

class OrganizationProfile(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='organization_profile',
        limit_choices_to={'user_type': UserType.ORGANIZATION}
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(validators=[MinLengthValidator(50)])
    organization_type = models.CharField(max_length=20, choices=OrganizationType.CHOICES)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='organizations')
    
    website_url = models.URLField(blank=True, null=True)
    social_media_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'organization_profiles'

    def __str__(self):
        return self.name