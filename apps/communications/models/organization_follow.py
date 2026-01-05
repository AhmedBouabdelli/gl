from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class OrganizationFollow(BaseModel):
    """
    Represents a volunteer following an organization
    
    Features:
    - One volunteer can follow many organizations
    - One organization can have many followers
    - Tracks follow date
    - Prevents duplicate follows (unique_together constraint)
    - Notification preferences per organization
    
    Design:
    - No redundant data stored
    - All data can be derived from relations
    - Indexed for fast queries
    """
    volunteer = models.ForeignKey(
        'accounts.VolunteerProfile',
        on_delete=models.CASCADE,
        related_name='following',
        help_text="Volunteer who is following"
    )
    
    organization = models.ForeignKey(
        'accounts.OrganizationProfile',
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="Organization being followed"
    )
    
    # Notification preferences (optional feature for future)
    notify_on_new_mission = models.BooleanField(
        default=True,
        help_text="Notify when organization creates new missions"
    )
    
    notify_on_updates = models.BooleanField(
        default=True,
        help_text="Notify about organization updates"
    )
    
    class Meta:
        db_table = 'organization_follows'
        ordering = ['-created_at']
        unique_together = [['volunteer', 'organization']]
        indexes = [
            models.Index(fields=['volunteer', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Organization Follow'
        verbose_name_plural = 'Organization Follows'
    
    def __str__(self):
        return f"{self.volunteer.user.get_full_name()} follows {self.organization.organization_name}"
    
    def clean(self):
        """Validate that volunteer doesn't follow themselves"""
        if hasattr(self.volunteer, 'user') and hasattr(self.organization, 'user'):
            if self.volunteer.user == self.organization.user:
                raise ValidationError("Cannot follow your own organization")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)