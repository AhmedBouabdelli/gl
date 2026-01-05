from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.missions.models import Mission, MissionSkill
from apps.core.constants import MissionStatus, RequirementLevel, ProficiencyLevel

class MissionService:
    
    @staticmethod
    def publish_mission(mission):
        """Publish a mission (change status from draft to published)"""
        if mission.status != MissionStatus.DRAFT:
            raise ValidationError("Only draft missions can be published")
        
        # Validate mission has required fields
        if not mission.mission_skills.filter(requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]).exists():
            raise ValidationError("Mission must have at least one required skill")
        
        mission.status = MissionStatus.PUBLISHED
        mission.published_at = timezone.now()
        mission.save()
        
        return mission
    
    @staticmethod
    def add_required_skill(mission, skill, requirement_level=RequirementLevel.REQUIRED, 
                          is_verification_required=False, min_proficiency=ProficiencyLevel.BEGINNER):
        """Add a required skill to a mission"""
        mission_skill, created = MissionSkill.objects.get_or_create(
            mission=mission,
            skill=skill,
            defaults={
                'requirement_level': requirement_level,
                'is_verification_required': is_verification_required,
                'min_proficiency_level': min_proficiency
            }
        )
        
        if not created:
            # Update existing mission skill
            mission_skill.requirement_level = requirement_level
            mission_skill.is_verification_required = is_verification_required
            mission_skill.min_proficiency_level = min_proficiency
            mission_skill.save()
        
        return mission_skill
    
    @staticmethod
    def get_eligible_volunteers(mission):
        """Get list of volunteers who meet mission requirements"""
        from apps.accounts.models import VolunteerProfile
        from apps.missions.services.participation_service import ParticipationService
        
        eligible_volunteers = []
        all_volunteers = VolunteerProfile.objects.filter(is_active=True)
        
        for volunteer in all_volunteers:
            can_apply, _ = ParticipationService.check_skill_requirements(mission, volunteer)
            if can_apply:
                eligible_volunteers.append(volunteer)
        
        return eligible_volunteers