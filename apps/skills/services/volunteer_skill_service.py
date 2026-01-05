from django.db import transaction, models
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from typing import List, Optional, Dict, Any, Set
from ..models import VolunteerSkill, Skill, VerificationRequest
from apps.core.constants import SkillVerificationStatus, ProficiencyLevel


class VolunteerSkillService:
    """Service for managing volunteer skills"""
    
    @staticmethod
    def get_volunteer_skills(
        volunteer_id: str,
        verification_status: Optional[str] = None,
        is_primary: Optional[bool] = None
    ) -> List[VolunteerSkill]:
        """Get all skills for a volunteer"""
        queryset = VolunteerSkill.objects.filter(
            volunteer_id=volunteer_id
        ).select_related(
            'skill',
            'skill__category',
            'verified_by'
        )

        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)

        if is_primary is not None:
            queryset = queryset.filter(is_primary=is_primary)

        return queryset.order_by('-is_primary', 'skill__name')

    @staticmethod
    def get_volunteer_skill_by_id(skill_id: str) -> Optional[VolunteerSkill]:
        """Get a specific volunteer skill by ID"""
        try:
            return VolunteerSkill.objects.select_related(
                'volunteer',
                'skill',
                'skill__category',
                'verified_by'
            ).get(id=skill_id)
        except VolunteerSkill.DoesNotExist:
            return None

    @staticmethod
    def get_verified_skill_ids(volunteer_id: str) -> Set[str]:
        """Get set of verified skill IDs for a volunteer"""
        verified_skills = VolunteerSkill.objects.filter(
            volunteer_id=volunteer_id,
            verification_status=SkillVerificationStatus.VERIFIED
        ).values_list('skill_id', flat=True)

        return set(str(skill_id) for skill_id in verified_skills)

    @staticmethod
    @transaction.atomic
    def add_skill_to_volunteer(
        volunteer_id: str,
        skill_id: str,
        proficiency_level: str = ProficiencyLevel.BEGINNER,
        last_used_date: Optional[str] = None,
        supporting_document: Optional[Any] = None,
        supporting_url: Optional[str] = None,
        is_primary: bool = False
    ) -> VolunteerSkill:
        """Add a skill to volunteer profile"""
        # Check if volunteer already has this skill
        if VolunteerSkill.objects.filter(
            volunteer_id=volunteer_id,
            skill_id=skill_id
        ).exists():
            raise ValidationError(
                "You already have this skill in your profile."
            )

        # Validate skill exists and is active
        try:
            skill = Skill.objects.get(id=skill_id, is_active=True)
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found or inactive.")

        # Validate proficiency level
        valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if proficiency_level not in valid_levels:
            raise ValidationError(f"Invalid proficiency level: {proficiency_level}")

        # If marking as primary, unset other primary skills
        if is_primary:
            VolunteerSkill.objects.filter(
                volunteer_id=volunteer_id,
                is_primary=True
            ).update(is_primary=False)

        # Determine initial verification status
        if skill.verification_requirement == Skill.VerificationRequirement.NONE:
            verification_status = SkillVerificationStatus.NOT_REQUIRED
        else:
            verification_status = SkillVerificationStatus.PENDING

        # Create volunteer skill
        volunteer_skill = VolunteerSkill.objects.create(
            volunteer_id=volunteer_id,
            skill=skill,
            proficiency_level=proficiency_level,
            verification_status=verification_status,
            last_used_date=last_used_date,
            supporting_document=supporting_document,
            supporting_url=supporting_url,
            verification_requested=False,
            verification_links=[],
            is_primary=is_primary
        )

        return volunteer_skill

    @staticmethod
    @transaction.atomic
    def update_volunteer_skill(
        volunteer_skill_id: str,
        volunteer_id: str,  # For authorization check
        proficiency_level: Optional[str] = None,
        last_used_date: Optional[str] = None,
        supporting_document: Optional[Any] = None,
        supporting_url: Optional[str] = None,
        is_primary: Optional[bool] = None
    ) -> VolunteerSkill:
        """Update a volunteer's skill"""
        try:
            volunteer_skill = VolunteerSkill.objects.select_related(
                'skill'
            ).get(id=volunteer_skill_id)
        except VolunteerSkill.DoesNotExist:
            raise ValidationError("Volunteer skill not found.")

        # Authorization check
        if str(volunteer_skill.volunteer_id) != str(volunteer_id):
            raise PermissionDenied("You can only update your own skills.")

        # Update proficiency level
        if proficiency_level:
            valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
            if proficiency_level not in valid_levels:
                raise ValidationError(f"Invalid proficiency level: {proficiency_level}")
            volunteer_skill.proficiency_level = proficiency_level

        # Update last used date
        if last_used_date is not None:
            volunteer_skill.last_used_date = last_used_date

        # Update supporting materials
        if supporting_document is not None:
            volunteer_skill.supporting_document = supporting_document

        if supporting_url is not None:
            volunteer_skill.supporting_url = supporting_url

        # Update primary status
        if is_primary is not None:
            if is_primary:
                # Unset other primary skills
                VolunteerSkill.objects.filter(
                    volunteer_id=volunteer_id,
                    is_primary=True
                ).exclude(id=volunteer_skill_id).update(is_primary=False)
            volunteer_skill.is_primary = is_primary

        volunteer_skill.save()
        return volunteer_skill

    @staticmethod
    @transaction.atomic
    def remove_skill_from_volunteer(
        volunteer_skill_id: str,
        volunteer_id: str
    ) -> Dict[str, Any]:
        """Remove a skill from volunteer profile"""
        try:
            volunteer_skill = VolunteerSkill.objects.get(id=volunteer_skill_id)
        except VolunteerSkill.DoesNotExist:
            raise ValidationError("Volunteer skill not found.")

        # Authorization check
        if str(volunteer_skill.volunteer_id) != str(volunteer_id):
            raise PermissionDenied("You can only remove your own skills.")

        # Also delete any verification requests for this skill
        VerificationRequest.objects.filter(volunteer_skill_id=volunteer_skill_id).delete()

        skill_name = volunteer_skill.skill.name
        volunteer_skill.delete()

        return {
            'deleted': True,
            'volunteer_skill_id': volunteer_skill_id,
            'skill_name': skill_name
        }

    @staticmethod
    @transaction.atomic
    def verify_skill(
        volunteer_skill_id: str,
        verifier_user_id: str,
        verification_status: str,
        verification_notes: Optional[str] = None
    ) -> VolunteerSkill:
        """Verify or reject a volunteer's skill"""
        try:
            volunteer_skill = VolunteerSkill.objects.select_related(
                'skill'
            ).get(id=volunteer_skill_id)
        except VolunteerSkill.DoesNotExist:
            raise ValidationError("Volunteer skill not found.")

        # Validate verification status
        if verification_status not in [
            SkillVerificationStatus.VERIFIED,
            SkillVerificationStatus.REJECTED
        ]:
            raise ValidationError(
                "Verification status must be VERIFIED or REJECTED."
            )

        # Check if skill requires verification
        if volunteer_skill.skill.verification_requirement == Skill.VerificationRequirement.NONE:
            raise ValidationError(
                "This skill does not require verification."
            )

        # Update verification details
        volunteer_skill.verification_status = verification_status
        volunteer_skill.verified_by_id = verifier_user_id
        volunteer_skill.verification_date = timezone.now()
        volunteer_skill.verification_notes = verification_notes

        # If verified, reset verification request flags
        if verification_status == SkillVerificationStatus.VERIFIED:
            volunteer_skill.verification_requested = False

        volunteer_skill.save()

        return volunteer_skill

    @staticmethod
    def check_skill_requirements_for_mission(
        volunteer_id: str,
        required_skill_ids: Set[str]
    ) -> Dict[str, Any]:
        """Check if volunteer has required skills for a mission"""
        if not required_skill_ids:
            return {
                'has_all_required': True,
                'missing_skills': [],
                'verified_skills': []
            }

        # Get volunteer's verified skills
        verified_skill_ids = VolunteerSkillService.get_verified_skill_ids(volunteer_id)

        # Find missing skills
        missing_skill_ids = required_skill_ids - verified_skill_ids

        # Get skill names for better error messages
        missing_skills = []
        if missing_skill_ids:
            missing_skills = list(
                Skill.objects.filter(
                    id__in=missing_skill_ids
                ).values_list('name', flat=True)
            )

        return {
            'has_all_required': len(missing_skill_ids) == 0,
            'missing_skills': missing_skills,
            'missing_skill_ids': list(missing_skill_ids),
            'verified_skills': list(verified_skill_ids),
            'required_skills': list(required_skill_ids)
        }

    @staticmethod
    def get_volunteer_skill_statistics(volunteer_id: str) -> Dict[str, Any]:
        """Get statistics about a volunteer's skills"""
        skills = VolunteerSkill.objects.filter(
            volunteer_id=volunteer_id
        ).select_related('skill', 'skill__category')

        total_skills = skills.count()
        verified = skills.filter(
            verification_status=SkillVerificationStatus.VERIFIED
        ).count()
        pending = skills.filter(
            verification_status=SkillVerificationStatus.PENDING
        ).count()
        pending_verification_requests = skills.filter(
            verification_requested=True
        ).count()

        # Proficiency distribution
        proficiency_counts = {}
        for skill in skills:
            level = skill.get_proficiency_level_display()
            proficiency_counts[level] = proficiency_counts.get(level, 0) + 1

        # Category distribution
        category_counts = {}
        for skill in skills:
            category = skill.skill.category.name
            category_counts[category] = category_counts.get(category, 0) + 1

        # Primary skill
        primary_skill = skills.filter(is_primary=True).first()

        return {
            'volunteer_id': volunteer_id,
            'total_skills': total_skills,
            'verified_skills': verified,
            'pending_verification': pending,
            'pending_verification_requests': pending_verification_requests,
            'proficiency_distribution': proficiency_counts,
            'category_distribution': category_counts,
            'primary_skill': primary_skill.skill.name if primary_skill else None,
        }

    @staticmethod
    def suggest_skills_for_volunteer(
        volunteer_id: str,
        limit: int = 5
    ) -> List[Skill]:
        """Suggest skills for a volunteer based on their current skills"""
        from django.db.models import Count
        
        # Get volunteer's current skill categories
        current_skills = VolunteerSkill.objects.filter(
            volunteer_id=volunteer_id
        ).select_related('skill__category')

        current_skill_ids = set(vs.skill_id for vs in current_skills)
        category_ids = set(vs.skill.category_id for vs in current_skills)

        # Suggest skills from same categories that volunteer doesn't have
        suggested_skills = Skill.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).exclude(
            id__in=current_skill_ids
        ).annotate(
            popularity=Count('volunteer_skills')
        ).order_by('-popularity')[:limit]

        return list(suggested_skills)

    @staticmethod
    def bulk_import_skills(
        volunteer_id: str,
        skills_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk import skills for a volunteer"""
        created = []
        failed = []

        for skill_data in skills_data:
            try:
                volunteer_skill = VolunteerSkillService.add_skill_to_volunteer(
                    volunteer_id=volunteer_id,
                    skill_id=skill_data.get('skill_id'),
                    proficiency_level=skill_data.get('proficiency_level', ProficiencyLevel.BEGINNER),
                    is_primary=skill_data.get('is_primary', False)
                )
                created.append({
                    'skill_id': str(volunteer_skill.skill_id),
                    'skill_name': volunteer_skill.skill.name
                })
            except (ValidationError, Exception) as e:
                failed.append({
                    'skill_id': skill_data.get('skill_id'),
                    'error': str(e)
                })

        return {
            'total_attempted': len(skills_data),
            'successfully_created': len(created),
            'failed': len(failed),
            'created_skills': created,
            'failed_skills': failed
        }