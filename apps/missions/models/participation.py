import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
from apps.accounts.models import VolunteerProfile
from apps.core.constants import ParticipationStatus
from .mission import Mission

class Participation(BaseModel):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='participations')
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='participations')
    
    status = models.CharField(max_length=20, choices=ParticipationStatus.CHOICES, default=ParticipationStatus.PENDING)
    application_message = models.TextField(blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(auto_now=True)
    
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, blank=True, null=True)
    review_notes = models.TextField(blank=True, null=True)
    
    actual_hours_worked = models.FloatField(blank=True, null=True)
    
    
    volunteer_rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Volunteer's rating to organization (1-5 stars)"
    )
    organization_rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Organization's rating to volunteer (1-5 stars)"
    )

    class Meta:
        db_table = 'participations'
        constraints = [
            models.UniqueConstraint(fields=['mission', 'volunteer'], name='unique_mission_volunteer'),
        ]
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['volunteer', 'status']),
            models.Index(fields=['volunteer_rating']),
            models.Index(fields=['organization_rating']),
        ]

    def __str__(self):
        return f"{self.volunteer.user.email} - {self.mission.title} ({self.status})"