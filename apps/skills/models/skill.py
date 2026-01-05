import uuid
from django.db import models
from apps.core.models import BaseModel
from .skill_category import SkillCategory

class Skill(BaseModel):
    class VerificationRequirement(models.TextChoices):
        NONE = 'none', 'No Verification Required'
        DOCUMENT = 'document', 'Document Verification'
        TEST = 'test', 'Skill Test Required'
        ENDORSEMENT = 'endorsement', 'Peer Endorsement Required'

    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.PROTECT, related_name='skills')
    verification_requirement = models.CharField(max_length=20, choices=VerificationRequirement.choices, default=VerificationRequirement.NONE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'skills'

    def __str__(self):
        return self.name