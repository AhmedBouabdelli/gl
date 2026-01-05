"""
Volunteer Search Service
Business logic for searching volunteers by skills
"""
from django.db.models import Q, Count, Prefetch
from typing import List, Dict, Any, Optional, Set
from apps.accounts.models import VolunteerProfile
from ..models import VolunteerSkill, MissionSkill, Skill
from apps.core.constants import SkillVerificationStatus, ProficiencyLevel


class VolunteerSearchService:
    """Service for searching volunteers by skills"""
    
    @staticmethod
    def search_volunteers_by_skills(
        skill_ids: List[str],
        verified_only: bool = True,
        min_proficiency_level: Optional[str] = None,
        match_type: str = 'all',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search volunteers who have specific skills
        
        Args:
            skill_ids: List of skill IDs to search for
            verified_only: Only include verified skills
            min_proficiency_level: Minimum proficiency level required
            match_type: 'all' (must have all skills) or 'any' (can have any skill)
            limit: Maximum number of results
            
        Returns:
            List of volunteer data with matched skills
        """
        # Build base query for volunteer skills
        skill_query = Q(volunteer_skills__skill_id__in=skill_ids)
        
        if verified_only:
            skill_query &= Q(volunteer_skills__verification_status=SkillVerificationStatus.VERIFIED)
        
        if min_proficiency_level:
            # Get proficiency levels greater than or equal to minimum
            proficiency_levels = VolunteerSearchService._get_proficiency_levels_gte(min_proficiency_level)
            skill_query &= Q(volunteer_skills__proficiency_level__in=proficiency_levels)
        
        # Get volunteers with annotations
        volunteers_queryset = VolunteerProfile.objects.filter(
            skill_query
        ).prefetch_related(
            Prefetch(
                'volunteer_skills',
                queryset=VolunteerSkill.objects.filter(
                    skill_id__in=skill_ids
                ).select_related('skill', 'skill__category')
            )
        ).annotate(
            matched_skill_count=Count('volunteer_skills', filter=Q(volunteer_skills__skill_id__in=skill_ids))
        ).distinct()
        
        # Filter based on match type
        if match_type == 'all':
            # Must have ALL skills
            volunteers_queryset = volunteers_queryset.filter(
                matched_skill_count=len(skill_ids)
            )
        
        # Order by number of matched skills (descending)
        volunteers_queryset = volunteers_queryset.order_by('-matched_skill_count')[:limit]
        
        # Build results
        results = []
        for volunteer in volunteers_queryset:
            # Get matched skills for this volunteer
            matched_skills = volunteer.volunteer_skills.filter(skill_id__in=skill_ids)
            
            skills_data = []
            for vs in matched_skills:
                skills_data.append({
                    'skill_id': str(vs.skill_id),
                    'skill_name': vs.skill.name,
                    'category': vs.skill.category.name,
                    'proficiency_level': vs.proficiency_level,
                    'proficiency_display': vs.get_proficiency_level_display(),
                    'verification_status': vs.verification_status,
                    'verification_display': vs.get_verification_status_display(),
                    'years_of_experience': float(vs.years_of_experience),
                    'is_primary': vs.is_primary,
                })
            
            results.append({
                'volunteer_id': str(volunteer.id),
                'volunteer_name': f"{volunteer.user.first_name} {volunteer.user.last_name}",
                'email': volunteer.user.email,
                'phone_number': volunteer.phone_number,
                'wilaya': volunteer.wilaya,
                'availability': volunteer.availability,
                'matched_skills_count': len(skills_data),
                'total_required_skills': len(skill_ids),
                'match_percentage': (len(skills_data) / len(skill_ids) * 100) if skill_ids else 0,
                'matched_skills': skills_data,
            })
        
        return results
    
    @staticmethod
    def find_volunteers_for_mission(
        mission_id: str,
        require_all_skills: bool = True,
        verified_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find volunteers that match mission skill requirements
        
        Args:
            mission_id: Mission ID
            require_all_skills: Only return volunteers with ALL required skills
            verified_only: Only consider verified skills
            limit: Maximum number of results
            
        Returns:
            List of volunteers with skill match information
        """
        # Get required and preferred skills for mission
        mission_skills = MissionSkill.objects.filter(
            mission_id=mission_id
        ).select_related('skill')
        
        required_skill_ids = [
            str(ms.skill_id) for ms in mission_skills 
            if ms.is_required_skill  # Uses model property
        ]
        
        preferred_skill_ids = [
            str(ms.skill_id) for ms in mission_skills 
            if not ms.is_required_skill
        ]
        
        all_skill_ids = required_skill_ids + preferred_skill_ids
        
        if not all_skill_ids:
            return []
        
        # Search volunteers with required skills
        search_skill_ids = required_skill_ids if required_skill_ids else all_skill_ids
        match_type = 'all' if require_all_skills else 'any'
        
        volunteers = VolunteerSearchService.search_volunteers_by_skills(
            skill_ids=search_skill_ids,
            verified_only=verified_only,
            match_type=match_type,
            limit=limit
        )
        
        # Enhance results with mission-specific matching info
        enhanced_results = []
        for volunteer_data in volunteers:
            volunteer_skill_ids = set(s['skill_id'] for s in volunteer_data['matched_skills'])
            
            # Calculate required skills match
            required_skills_matched = set(required_skill_ids) & volunteer_skill_ids
            required_skills_missing = set(required_skill_ids) - volunteer_skill_ids
            
            # Calculate preferred skills match
            preferred_skills_matched = set(preferred_skill_ids) & volunteer_skill_ids
            
            # Calculate overall match score
            required_weight = 0.7
            preferred_weight = 0.3
            
            required_score = (
                len(required_skills_matched) / len(required_skill_ids) * 100 
                if required_skill_ids else 100
            )
            preferred_score = (
                len(preferred_skills_matched) / len(preferred_skill_ids) * 100 
                if preferred_skill_ids else 0
            )
            
            overall_score = (required_score * required_weight) + (preferred_score * preferred_weight)
            
            enhanced_results.append({
                **volunteer_data,
                'mission_match': {
                    'overall_score': round(overall_score, 2),
                    'required_skills_matched': len(required_skills_matched),
                    'required_skills_total': len(required_skill_ids),
                    'required_skills_missing': len(required_skills_missing),
                    'preferred_skills_matched': len(preferred_skills_matched),
                    'preferred_skills_total': len(preferred_skill_ids),
                    'is_fully_qualified': len(required_skills_missing) == 0,
                }
            })
        
        # Sort by overall match score
        enhanced_results.sort(key=lambda x: x['mission_match']['overall_score'], reverse=True)
        
        return enhanced_results
    
    @staticmethod
    def search_volunteers_by_category(
        category_id: str,
        verified_only: bool = True,
        min_proficiency_level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search volunteers who have skills in a specific category
        
        Args:
            category_id: Skill category ID
            verified_only: Only include verified skills
            min_proficiency_level: Minimum proficiency level
            limit: Maximum number of results
            
        Returns:
            List of volunteers with skills in the category
        """
        # Get all skills in this category
        skills_in_category = Skill.objects.filter(
            category_id=category_id,
            is_active=True
        ).values_list('id', flat=True)
        
        skill_ids = [str(sid) for sid in skills_in_category]
        
        if not skill_ids:
            return []
        
        # Search volunteers with any of these skills
        return VolunteerSearchService.search_volunteers_by_skills(
            skill_ids=skill_ids,
            verified_only=verified_only,
            min_proficiency_level=min_proficiency_level,
            match_type='any',
            limit=limit
        )
    
    @staticmethod
    def _get_proficiency_levels_gte(min_level: str) -> List[str]:
        """
        Get proficiency levels greater than or equal to minimum level
        
        Args:
            min_level: Minimum proficiency level
            
        Returns:
            List of proficiency level codes
        """
        level_order = {
            ProficiencyLevel.BEGINNER: 1,
            ProficiencyLevel.INTERMEDIATE: 2,
            ProficiencyLevel.ADVANCED: 3,
            ProficiencyLevel.EXPERT: 4,
        }
        
        min_value = level_order.get(min_level, 1)
        
        return [
            level for level, value in level_order.items()
            if value >= min_value
        ]