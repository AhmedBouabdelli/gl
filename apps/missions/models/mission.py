import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
from apps.core.constants import (
    MissionStatus,
    MissionType,
    ProficiencyLevel
)

class Mission(BaseModel):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    
    # ✅ FIXED: Use string references for all ForeignKeys
    organization = models.ForeignKey(
        'accounts.OrganizationProfile', 
        on_delete=models.CASCADE, 
        related_name='missions'
    )
    
    mission_type = models.CharField(max_length=20, choices=MissionType.CHOICES, default=MissionType.ONE_TIME)
    proficiency_level = models.CharField(max_length=20, choices=ProficiencyLevel.CHOICES, default=ProficiencyLevel.INTERMEDIATE)
    
    # ✅ FIXED: Use string reference to avoid circular import
    sdg = models.ForeignKey(
        'skills.SustainableDevelopmentGoal', 
        on_delete=models.PROTECT, 
        related_name='missions'
    )
    
    
    address = models.ForeignKey(
        'accounts.Address', 
        on_delete=models.PROTECT, 
        related_name='missions'
    )
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    application_deadline = models.DateTimeField()
    estimated_total_hours = models.PositiveIntegerField()
    volunteers_needed = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    volunteers_approved = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=MissionStatus.CHOICES, default=MissionStatus.DRAFT)
    is_featured = models.BooleanField(default=False)
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional mission context"
    )
    
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'missions'
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['organization', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='end_date_after_start_date'
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

    def get_sdg_object(self):
        """Lazy load the SDG object when needed"""
        from apps.skills.models import SustainableDevelopmentGoal
        return SustainableDevelopmentGoal.objects.get(pk=self.sdg_id)

    def get_organization_object(self):
        """Lazy load the organization object when needed"""
        from apps.accounts.models import OrganizationProfile
        return OrganizationProfile.objects.get(pk=self.organization_id)

    def get_address_object(self):
        """Lazy load the address object when needed"""
        from apps.accounts.models import Address
        return Address.objects.get(pk=self.address_id)