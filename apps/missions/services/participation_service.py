from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.missions.models import Participation, MissionSkill
from apps.accounts.models import VolunteerProfile
from apps.core.constants import ParticipationStatus, SkillVerificationStatus, RequirementLevel, ProficiencyLevel

class ParticipationService:
    
    @staticmethod
    def check_skill_requirements(mission, volunteer):
        """
        Check if volunteer meets all mission skill requirements
        Returns: (can_apply: bool, missing_requirements: list)
        """
        missing_requirements = []
        
        # Get required skills for this mission
        required_skills = MissionSkill.objects.filter(
            mission=mission,
            requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
        )
        
        for mission_skill in required_skills:
            # Check if volunteer has this skill
            volunteer_skill = volunteer.volunteer_skills.filter(
                skill=mission_skill.skill
            ).first()
            
            if not volunteer_skill:
                missing_requirements.append(f"Missing required skill: {mission_skill.skill.name}")
                continue
            
            # Check verification if required
            if (mission_skill.is_verification_required and 
                volunteer_skill.verification_status != SkillVerificationStatus.VERIFIED):
                missing_requirements.append(f"Skill verification required for: {mission_skill.skill.name}")
                continue
            
            # Check proficiency level using order comparison
            proficiency_order = {
                ProficiencyLevel.BEGINNER: 1,
                ProficiencyLevel.INTERMEDIATE: 2,
                ProficiencyLevel.ADVANCED: 3,
                ProficiencyLevel.EXPERT: 4
            }
            
            volunteer_level = volunteer_skill.proficiency_level
            required_level = mission_skill.min_proficiency_level
            
            if proficiency_order[volunteer_level] < proficiency_order[required_level]:
                missing_requirements.append(
                    f"Insufficient proficiency in {mission_skill.skill.name}. "
                    f"Required: {mission_skill.get_min_proficiency_level_display()}, "
                    f"You have: {volunteer_skill.get_proficiency_level_display()}"
                )
                continue
        
        can_apply = len(missing_requirements) == 0
        return can_apply, missing_requirements
    
    @staticmethod
    def create_participation(mission, volunteer, application_message=""):
        """
        Create a new participation after validating requirements
        """
        # Check if mission is open for applications
        if mission.status != 'published':
            raise ValidationError("This mission is not currently accepting applications")
        
        if mission.application_deadline < timezone.now():
            raise ValidationError("Application deadline has passed")
        
        # Check skill requirements
        can_apply, missing_requirements = ParticipationService.check_skill_requirements(mission, volunteer)
        
        if not can_apply:
            raise ValidationError({
                'message': 'Cannot apply to mission - skill requirements not met',
                'missing_requirements': missing_requirements
            })
        
        # Check for existing application
        existing_participation = Participation.objects.filter(
            mission=mission,
            volunteer=volunteer
        ).first()
        
        if existing_participation:
            raise ValidationError("You have already applied to this mission")
        
        # Check if mission has available slots
        current_approved = mission.participations.filter(
            status=ParticipationStatus.ACCEPTED
        ).count()
        
        if current_approved >= mission.volunteers_needed:
            raise ValidationError("Mission is full - no available slots")
        
        # Create participation
        participation = Participation.objects.create(
            mission=mission,
            volunteer=volunteer,
            application_message=application_message,
            status=ParticipationStatus.PENDING
        )
        
        return participation
    
    @staticmethod
    def get_mission_requirements_summary(mission, volunteer):
        """
        Get detailed requirements summary for a mission
        """
        requirements = MissionSkill.objects.filter(mission=mission)
        
        summary = {
            'mission_title': mission.title,
            'required_skills': [],
            'preferred_skills': [],
            'volunteer_qualifications': [],
            'missing_requirements': []
        }
        
        can_apply, missing_reqs = ParticipationService.check_skill_requirements(mission, volunteer)
        summary['can_apply'] = can_apply
        summary['missing_requirements'] = missing_reqs
        
        for req in requirements:
            volunteer_skill = volunteer.volunteer_skills.filter(skill=req.skill).first()
            
            skill_info = {
                'skill_name': req.skill.name,
                'requirement_level': req.get_requirement_level_display(),
                'verification_required': req.is_verification_required,
                'min_proficiency': req.get_min_proficiency_level_display(),
                'volunteer_has_skill': volunteer_skill is not None,
                'volunteer_proficiency': volunteer_skill.get_proficiency_level_display() if volunteer_skill else 'Not known',
                'is_verified': volunteer_skill.verification_status == SkillVerificationStatus.VERIFIED if volunteer_skill else False
            }
            
            if req.requirement_level in [RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]:
                summary['required_skills'].append(skill_info)
            else:
                summary['preferred_skills'].append(skill_info)
        
        return summary