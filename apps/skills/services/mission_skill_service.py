
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict, Any, Set
from ..models import MissionSkill, Skill
from apps.core.constants import RequirementLevel, ProficiencyLevel


class MissionSkillService:
   

    @staticmethod
    def get_mission_skills(
        mission_id: str,
        requirement_level: Optional[str] = None,
        is_verification_required: Optional[bool] = None
    ) -> List[MissionSkill]:
    
        queryset = MissionSkill.objects.filter(
            mission_id=mission_id
        ).select_related('skill', 'skill__category')

        if requirement_level:
            queryset = queryset.filter(requirement_level=requirement_level)

        if is_verification_required is not None:
            queryset = queryset.filter(is_verification_required=is_verification_required)

        return queryset.order_by('-requirement_level', 'skill__name')

    @staticmethod
    def get_required_skill_ids(mission_id: str, verified_only: bool = True) -> Set[str]:
       
        queryset = MissionSkill.objects.filter(
            mission_id=mission_id,
            requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
        )

        if verified_only:
            queryset = queryset.filter(is_verification_required=True)

        skill_ids = queryset.values_list('skill_id', flat=True)
        return set(str(skill_id) for skill_id in skill_ids)

    @staticmethod
    @transaction.atomic
    def add_skill_to_mission(
        mission_id: str,
        skill_id: str,
        requirement_level: str = RequirementLevel.PREFERRED,
        is_verification_required: bool = False,
        min_proficiency_level: str = ProficiencyLevel.BEGINNER
    ) -> MissionSkill:
       
        # Check if mission already has this skill
        if MissionSkill.objects.filter(
            mission_id=mission_id,
            skill_id=skill_id
        ).exists():
            raise ValidationError(
                "This skill is already added to the mission."
            )

        # Validate skill exists and is active
        try:
            skill = Skill.objects.get(id=skill_id, is_active=True)
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found or inactive.")

        # Validate requirement level
        valid_levels = [choice[0] for choice in RequirementLevel.CHOICES]
        if requirement_level not in valid_levels:
            raise ValidationError(f"Invalid requirement level: {requirement_level}")

        # Validate proficiency level
        valid_proficiency = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if min_proficiency_level not in valid_proficiency:
            raise ValidationError(f"Invalid proficiency level: {min_proficiency_level}")

        # Create mission skill
        mission_skill = MissionSkill.objects.create(
            mission_id=mission_id,
            skill=skill,
            requirement_level=requirement_level,
            is_verification_required=is_verification_required,
            min_proficiency_level=min_proficiency_level
        )

        return mission_skill

    @staticmethod
    @transaction.atomic
    def update_mission_skill(
        mission_skill_id: str,
        requirement_level: Optional[str] = None,
        is_verification_required: Optional[bool] = None,
        min_proficiency_level: Optional[str] = None
    ) -> MissionSkill:
        
        try:
            mission_skill = MissionSkill.objects.select_related('skill').get(
                id=mission_skill_id
            )
        except MissionSkill.DoesNotExist:
            raise ValidationError("Mission skill not found.")

        # Update requirement level
        if requirement_level:
            valid_levels = [choice[0] for choice in RequirementLevel.CHOICES]
            if requirement_level not in valid_levels:
                raise ValidationError(f"Invalid requirement level: {requirement_level}")
            mission_skill.requirement_level = requirement_level

        # Update verification requirement
        if is_verification_required is not None:
            mission_skill.is_verification_required = is_verification_required

        # Update proficiency level
        if min_proficiency_level:
            valid_proficiency = [choice[0] for choice in ProficiencyLevel.CHOICES]
            if min_proficiency_level not in valid_proficiency:
                raise ValidationError(f"Invalid proficiency level: {min_proficiency_level}")
            mission_skill.min_proficiency_level = min_proficiency_level

        mission_skill.save()
        return mission_skill

    @staticmethod
    @transaction.atomic
    def remove_skill_from_mission(
        mission_skill_id: str,
        mission_id: str  # For authorization
    ) -> Dict[str, Any]:
       
        try:
            mission_skill = MissionSkill.objects.get(id=mission_skill_id)
        except MissionSkill.DoesNotExist:
            raise ValidationError("Mission skill not found.")

        # Authorization check
        if str(mission_skill.mission_id) != str(mission_id):
            raise ValidationError("Cannot remove skill from another mission.")

        skill_name = mission_skill.skill.name
        mission_skill.delete()

        return {
            'deleted': True,
            'mission_skill_id': mission_skill_id,
            'skill_name': skill_name
        }

    @staticmethod
    def validate_volunteer_for_mission(
        volunteer_verified_skills: Set[str],
        mission_id: str
    ) -> Dict[str, Any]:
       
        # Get required skills for mission
        required_skills = MissionSkill.objects.filter(
            mission_id=mission_id,
            requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL],
            is_verification_required=True
        ).select_related('skill')

        # Check which required skills are missing
        missing_skills = []
        for mission_skill in required_skills:
            if str(mission_skill.skill_id) not in volunteer_verified_skills:
                missing_skills.append({
                    'skill_name': mission_skill.skill.name,
                    'requirement_level': mission_skill.get_requirement_level_display(),
                    'min_proficiency': mission_skill.get_min_proficiency_level_display()
                })

        has_all_required = len(missing_skills) == 0

        return {
            'can_apply': has_all_required,
            'has_all_required': has_all_required,
            'missing_skills': missing_skills,
            'total_required_skills': required_skills.count(),
            'missing_count': len(missing_skills)
        }

    @staticmethod
    def get_mission_skill_statistics(mission_id: str) -> Dict[str, Any]:
       
        skills = MissionSkill.objects.filter(
            mission_id=mission_id
        ).select_related('skill', 'skill__category')

        total_skills = skills.count()
        
        # Count by requirement level
        requirement_breakdown = {}
        for level_code, level_name in RequirementLevel.CHOICES:
            count = skills.filter(requirement_level=level_code).count()
            if count > 0:
                requirement_breakdown[level_name] = count

        # Count verification required
        verification_required_count = skills.filter(
            is_verification_required=True
        ).count()

        # Count by category
        category_breakdown = {}
        for skill in skills:
            category = skill.skill.category.name
            category_breakdown[category] = category_breakdown.get(category, 0) + 1

        # Get critical and required skills
        critical_skills = list(
            skills.filter(
                requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
            ).values_list('skill__name', flat=True)
        )

        return {
            'mission_id': mission_id,
            'total_skills': total_skills,
            'requirement_breakdown': requirement_breakdown,
            'verification_required_count': verification_required_count,
            'category_breakdown': category_breakdown,
            'critical_skills': critical_skills,
            'critical_skills_count': len(critical_skills)
        }

    @staticmethod
    def bulk_add_skills_to_mission(
        mission_id: str,
        skills_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        created = []
        failed = []

        for skill_data in skills_data:
            try:
                mission_skill = MissionSkillService.add_skill_to_mission(
                    mission_id=mission_id,
                    skill_id=skill_data.get('skill_id'),
                    requirement_level=skill_data.get('requirement_level', RequirementLevel.PREFERRED),
                    is_verification_required=skill_data.get('is_verification_required', False),
                    min_proficiency_level=skill_data.get('min_proficiency_level', ProficiencyLevel.BEGINNER)
                )
                created.append({
                    'skill_id': str(mission_skill.skill_id),
                    'skill_name': mission_skill.skill.name
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

    @staticmethod
    def suggest_skills_for_mission(
        mission_id: str,
        limit: int = 5
    ) -> List[Skill]:
        
        from django.db.models import Count
        
        # Get current mission skills
        current_skills = MissionSkill.objects.filter(
            mission_id=mission_id
        ).select_related('skill__category')

        current_skill_ids = set(ms.skill_id for ms in current_skills)
        category_ids = set(ms.skill.category_id for ms in current_skills)

        # Suggest popular skills from same categories
        suggested_skills = Skill.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).exclude(
            id__in=current_skill_ids
        ).annotate(
            mission_count=Count('mission_skills')
        ).order_by('-mission_count')[:limit]

        return list(suggested_skills)