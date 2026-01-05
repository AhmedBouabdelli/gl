from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.skills.models import VolunteerSkill
from apps.core.constants import SkillVerificationStatus

class SkillVerificationService:
    
    @staticmethod
    def verify_skill(volunteer_skill, verified_by_user, notes=""):
        """Verify a volunteer's skill"""
        if volunteer_skill.verification_status == SkillVerificationStatus.VERIFIED:
            raise ValidationError("Skill is already verified")
        
        volunteer_skill.verification_status = SkillVerificationStatus.VERIFIED
        volunteer_skill.verified_by = verified_by_user
        volunteer_skill.verification_date = timezone.now()
        volunteer_skill.verification_notes = notes
        volunteer_skill.save()
        
        return volunteer_skill
    
    @staticmethod
    def reject_skill_verification(volunteer_skill, rejected_by_user, notes=""):
        """Reject a skill verification request"""
        volunteer_skill.verification_status = SkillVerificationStatus.REJECTED
        volunteer_skill.verified_by = rejected_by_user
        volunteer_skill.verification_date = timezone.now()
        volunteer_skill.verification_notes = notes
        volunteer_skill.save()
        
        return volunteer_skill
    
    @staticmethod
    def get_verification_requirements(skill):
        """Get verification requirements for a skill"""
        return {
            'skill_name': skill.name,
            'verification_required': skill.verification_requirement != 'none',
            'verification_type': skill.get_verification_requirement_display(),
            'description': skill.description
        }