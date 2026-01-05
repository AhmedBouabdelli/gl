import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import SkillVerificationStatus, ProficiencyLevel
from apps.accounts.models import VolunteerProfile
from .skill import Skill

class VolunteerSkill(BaseModel):
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='volunteer_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='volunteer_skills')
    
    proficiency_level = models.CharField(max_length=20, choices=ProficiencyLevel.CHOICES, default=ProficiencyLevel.BEGINNER)
    verification_status = models.CharField(max_length=20, choices=SkillVerificationStatus.CHOICES, default=SkillVerificationStatus.PENDING)
    
    verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_skills')
    verification_date = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Verification request fields
    verification_requested = models.BooleanField(default=False)
    verification_request_date = models.DateTimeField(blank=True, null=True)
    verification_documents = models.FileField(upload_to='skill_verification_docs/', blank=True, null=True)
    verification_links = models.JSONField(default=list, blank=True)  # Store multiple URLs
    
    # Original fields
    supporting_document = models.FileField(upload_to='skill_verifications/', blank=True, null=True)
    supporting_url = models.URLField(blank=True, null=True)
    
    last_used_date = models.DateField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'volunteer_skills'
        constraints = [
            models.UniqueConstraint(fields=['volunteer', 'skill'], name='unique_volunteer_skill'),
        ]

    def __str__(self):
        return f"{self.volunteer.user.email} - {self.skill.name} ({self.verification_status})"

    def can_request_verification(self):
        """Check if verification can be requested"""
        return (
            self.skill.verification_requirement != Skill.VerificationRequirement.NONE and
            self.verification_status == SkillVerificationStatus.PENDING and
            not self.verification_requested
        )
    
    def request_verification(self, documents=None, links=None):
        """Request verification for this skill"""
        self.verification_requested = True
        self.verification_request_date = timezone.now()
        if documents:
            self.verification_documents = documents
        if links:
            self.verification_links = links
        self.save()