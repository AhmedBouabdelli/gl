import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import SkillVerificationStatus
from .volunteer_skill import VolunteerSkill

class VerificationRequest(BaseModel):
    """Track verification requests and their status"""
    volunteer_skill = models.ForeignKey(VolunteerSkill, on_delete=models.CASCADE, related_name='verification_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    request_documents = models.FileField(upload_to='verification_requests/', blank=True, null=True)
    request_links = models.JSONField(default=list, blank=True)
    request_notes = models.TextField(blank=True)
    
    # Admin review fields
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_verifications')
    review_date = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_more_info', 'Needs More Information'),
    ], default='pending')
    review_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)  # Internal notes
    
    class Meta:
        db_table = 'verification_requests'
        ordering = ['-request_date']

    def __str__(self):
        return f"Verification Request for {self.volunteer_skill}"
    
    @property
    def volunteer(self):
        return self.volunteer_skill.volunteer
    
    @property
    def skill(self):
        return self.volunteer_skill.skill