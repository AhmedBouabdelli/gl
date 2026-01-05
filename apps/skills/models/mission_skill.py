import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import RequirementLevel, ProficiencyLevel

class MissionSkill(BaseModel):
    # ✅ FIXED: Use string references to avoid circular imports
    mission = models.ForeignKey(
        'missions.Mission', 
        on_delete=models.CASCADE, 
        related_name='mission_skills'
    )
    skill = models.ForeignKey(
        'skills.Skill', 
        on_delete=models.CASCADE, 
        related_name='mission_skills'
    )
    
    requirement_level = models.CharField(
        max_length=20, 
        choices=RequirementLevel.CHOICES, 
        default=RequirementLevel.PREFERRED
    )
    is_verification_required = models.BooleanField(default=False)
    min_proficiency_level = models.CharField(
        max_length=20, 
        choices=ProficiencyLevel.CHOICES, 
        default=ProficiencyLevel.BEGINNER
    )

    class Meta:
        db_table = 'mission_skills'
        constraints = [
            models.UniqueConstraint(
                fields=['mission', 'skill'], 
                name='unique_mission_skill'
            ),
        ]

    def __str__(self):
        return f"{self.mission.title} - {self.skill.name} ({self.requirement_level})"

    @property
    def is_required_skill(self):
        """Check if this skill is required (not just preferred)"""
        return self.requirement_level in [RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]

    def get_mission_object(self):
        """Lazy load the mission object when needed"""
        from apps.missions.models import Mission
        return Mission.objects.get(pk=self.mission_id)

    def get_skill_object(self):
        """Lazy load the skill object when needed"""
        from apps.skills.models import Skill
        return Skill.objects.get(pk=self.skill_id)

    @property
    def mission_title(self):
        """Access mission title without loading full object"""
        return self.mission.title

    @property  
    def skill_name(self):
        """Access skill name without loading full object"""
        return self.skill.name