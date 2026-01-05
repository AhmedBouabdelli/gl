
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict, Any
from ..models import Skill, SkillCategory


class SkillService:
   

    @staticmethod
    def get_all_skills(
        category_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        verification_required: Optional[bool] = None
    ) -> List[Skill]:
       
        queryset = Skill.objects.select_related('category')

        # Apply filters
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if verification_required is not None:
            if verification_required:
                queryset = queryset.exclude(
                    verification_requirement=Skill.VerificationRequirement.NONE
                )
            else:
                queryset = queryset.filter(
                    verification_requirement=Skill.VerificationRequirement.NONE
                )

        return queryset.order_by('name')

    @staticmethod
    def get_skill_by_id(skill_id: str) -> Optional[Skill]:
       
        try:
            return Skill.objects.select_related('category').prefetch_related(
                'volunteer_skills',
                'mission_skills'
            ).get(id=skill_id)
        except Skill.DoesNotExist:
            return None

    @staticmethod
    def get_popular_skills(limit: int = 10) -> List[Skill]:
       
        return Skill.objects.filter(
            is_active=True
        ).annotate(
            volunteer_count=Count('volunteer_skills')
        ).order_by('-volunteer_count')[:limit]

    @staticmethod
    @transaction.atomic
    def create_skill(
        name: str,
        category_id: str,
        description: Optional[str] = None,
        verification_requirement: str = Skill.VerificationRequirement.NONE,
        is_active: bool = True
    ) -> Skill:
        
        # Validate name
        name = name.strip().title()
        if Skill.objects.filter(name__iexact=name).exists():
            raise ValidationError(
                f"Skill with name '{name}' already exists."
            )

        # Validate category
        try:
            category = SkillCategory.objects.get(id=category_id)
        except SkillCategory.DoesNotExist:
            raise ValidationError("Category not found.")

        # Validate verification requirement
        valid_requirements = [choice[0] for choice in Skill.VerificationRequirement.choices]
        if verification_requirement not in valid_requirements:
            raise ValidationError(
                f"Invalid verification requirement: {verification_requirement}"
            )

        # Create skill
        skill = Skill.objects.create(
            name=name,
            category=category,
            description=description,
            verification_requirement=verification_requirement,
            is_active=is_active
        )

        return skill

    @staticmethod
    @transaction.atomic
    def update_skill(
        skill_id: str,
        name: Optional[str] = None,
        category_id: Optional[str] = None,
        description: Optional[str] = None,
        verification_requirement: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Skill:
      
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found.")

        # Update name if provided
        if name:
            name = name.strip().title()
            if Skill.objects.filter(
                name__iexact=name
            ).exclude(id=skill_id).exists():
                raise ValidationError(
                    f"Skill with name '{name}' already exists."
                )
            skill.name = name

        # Update category if provided
        if category_id:
            try:
                category = SkillCategory.objects.get(id=category_id)
                skill.category = category
            except SkillCategory.DoesNotExist:
                raise ValidationError("Category not found.")

        # Update description if provided
        if description is not None:
            skill.description = description

        # Update verification requirement if provided
        if verification_requirement:
            valid_requirements = [choice[0] for choice in Skill.VerificationRequirement.choices]
            if verification_requirement not in valid_requirements:
                raise ValidationError(
                    f"Invalid verification requirement: {verification_requirement}"
                )
            skill.verification_requirement = verification_requirement

        # Update active status if provided
        if is_active is not None:
            skill.is_active = is_active

        skill.save()
        return skill

    @staticmethod
    @transaction.atomic
    def activate_skill(skill_id: str) -> Skill:
      
        try:
            skill = Skill.objects.get(id=skill_id)
            skill.is_active = True
            skill.save()
            return skill
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found.")

    @staticmethod
    @transaction.atomic
    def deactivate_skill(skill_id: str) -> Skill:
      
        try:
            skill = Skill.objects.get(id=skill_id)
            skill.is_active = False
            skill.save()
            return skill
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found.")

    @staticmethod
    @transaction.atomic
    def delete_skill(skill_id: str, force: bool = False) -> Dict[str, Any]:
        
        try:
            skill = Skill.objects.prefetch_related(
                'volunteer_skills',
                'mission_skills'
            ).get(id=skill_id)
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found.")

        volunteer_count = skill.volunteer_skills.count()
        mission_count = skill.mission_skills.count()

        if not force and (volunteer_count > 0 or mission_count > 0):
            raise ValidationError(
                f"Cannot delete skill used by {volunteer_count} volunteers "
                f"and {mission_count} missions. Use force=True to override."
            )

        skill_name = skill.name
        skill.delete()

        return {
            'deleted': True,
            'skill_id': skill_id,
            'skill_name': skill_name,
            'affected_volunteers': volunteer_count,
            'affected_missions': mission_count
        }

    @staticmethod
    def search_skills(query: str, category_id: Optional[str] = None) -> List[Skill]:
     
        if not query:
            return []

        queryset = Skill.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.select_related('category').order_by('name')

    @staticmethod
    def get_skill_statistics(skill_id: str) -> Dict[str, Any]:
  
        try:
            skill = Skill.objects.prefetch_related(
                'volunteer_skills',
                'mission_skills'
            ).get(id=skill_id)
        except Skill.DoesNotExist:
            raise ValidationError("Skill not found.")

        # Count volunteers by verification status
        volunteer_stats = skill.volunteer_skills.values(
            'verification_status'
        ).annotate(count=Count('id'))

        verification_breakdown = {
            stat['verification_status']: stat['count']
            for stat in volunteer_stats
        }

        # Count missions by requirement level
        mission_stats = skill.mission_skills.values(
            'requirement_level'
        ).annotate(count=Count('id'))

        requirement_breakdown = {
            stat['requirement_level']: stat['count']
            for stat in mission_stats
        }

        return {
            'skill_id': str(skill.id),
            'skill_name': skill.name,
            'category': skill.category.name,
            'is_active': skill.is_active,
            'verification_requirement': skill.get_verification_requirement_display(),
            'total_volunteers': skill.volunteer_skills.count(),
            'verification_breakdown': verification_breakdown,
            'total_missions': skill.mission_skills.count(),
            'requirement_breakdown': requirement_breakdown
        }

    @staticmethod
    def get_skills_by_category(category_id: str, active_only: bool = True) -> List[Skill]:
     
        queryset = Skill.objects.filter(category_id=category_id)

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by('name')