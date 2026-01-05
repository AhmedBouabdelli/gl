"""
Volunteer Search ViewSet with Updated Permissions
Allows organizations and admins to search volunteers by skills
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import VolunteerProfile
from ..models import VolunteerSkill
from ..services import VolunteerSearchService
from ..serializers import (
    VolunteerSearchResultSerializer,
    VolunteerSkillMatchSerializer,
)
from apps.core.permissions import (
    CanSearchVolunteers,
    get_volunteer_search_permissions
)


class VolunteerSearchViewSet(viewsets.ViewSet):
    """
    ViewSet for searching volunteers by skills
    
    Permissions:
    - Organization accounts can search volunteers
    - Admin accounts can search volunteers
    - Volunteer accounts CANNOT search other volunteers (privacy protection)
    
    Endpoints:
    - GET /volunteer-search/by_skills/ - Search volunteers by skill IDs
    - GET /volunteer-search/by_mission/ - Find matching volunteers for mission
    - GET /volunteer-search/by_skill_category/ - Search volunteers by skill category
    """
    
    def get_permissions(self):
        """
        Only organizations and admins can search volunteers
        Uses CanSearchVolunteers permission which enforces:
        - Admins: Full access
        - Organizations: Can search
        - Volunteers: Denied (privacy protection)
        """
        return get_volunteer_search_permissions(self.action)
    
    @action(detail=False, methods=['get'])
    def by_skills(self, request):
        """
        Search volunteers by skill IDs [Organization/Admin only]
        
        Query Parameters:
        - skill_ids: Comma-separated list of skill UUIDs (required)
        - verified_only: true/false (default: true)
        - min_proficiency: beginner/intermediate/advanced/expert (optional)
        - match_type: all/any (default: all)
          - all: Volunteer must have ALL specified skills
          - any: Volunteer can have ANY of the specified skills
        - limit: Number of results (default: 50)
        
        Example:
        GET /volunteer-search/by_skills/?skill_ids=uuid1,uuid2,uuid3&verified_only=true&match_type=all
        """
        # Get query parameters
        skill_ids_param = request.query_params.get('skill_ids', '')
        if not skill_ids_param:
            return Response(
                {'error': 'skill_ids parameter is required (comma-separated UUIDs)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        skill_ids = [sid.strip() for sid in skill_ids_param.split(',') if sid.strip()]
        if not skill_ids:
            return Response(
                {'error': 'At least one skill_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        verified_only = request.query_params.get('verified_only', 'true').lower() == 'true'
        min_proficiency = request.query_params.get('min_proficiency', None)
        match_type = request.query_params.get('match_type', 'all').lower()
        limit = int(request.query_params.get('limit', 50))
        
        if match_type not in ['all', 'any']:
            return Response(
                {'error': 'match_type must be "all" or "any"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Search volunteers
            results = VolunteerSearchService.search_volunteers_by_skills(
                skill_ids=skill_ids,
                verified_only=verified_only,
                min_proficiency_level=min_proficiency,
                match_type=match_type,
                limit=limit
            )
            
            serializer = VolunteerSearchResultSerializer(results, many=True)
            return Response({
                'count': len(results),
                'search_criteria': {
                    'skill_ids': skill_ids,
                    'verified_only': verified_only,
                    'min_proficiency': min_proficiency,
                    'match_type': match_type,
                },
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_mission(self, request):
        """
        Find volunteers that match mission skill requirements [Organization/Admin only]
        
        Query Parameters:
        - mission_id: Mission UUID (required)
        - require_all: true/false (default: true)
          - true: Only show volunteers who have ALL required skills
          - false: Show all volunteers with match percentage
        - verified_only: true/false (default: true)
        - limit: Number of results (default: 50)
        
        Example:
        GET /volunteer-search/by_mission/?mission_id=uuid&require_all=true
        """
        mission_id = request.query_params.get('mission_id')
        if not mission_id:
            return Response(
                {'error': 'mission_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        require_all = request.query_params.get('require_all', 'true').lower() == 'true'
        verified_only = request.query_params.get('verified_only', 'true').lower() == 'true'
        limit = int(request.query_params.get('limit', 50))
        
        try:
            # Find matching volunteers for mission
            results = VolunteerSearchService.find_volunteers_for_mission(
                mission_id=mission_id,
                require_all_skills=require_all,
                verified_only=verified_only,
                limit=limit
            )
            
            serializer = VolunteerSkillMatchSerializer(results, many=True)
            return Response({
                'count': len(results),
                'mission_id': mission_id,
                'search_criteria': {
                    'require_all_skills': require_all,
                    'verified_only': verified_only,
                },
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_skill_category(self, request):
        """
        Search volunteers by skill category [Organization/Admin only]
        
        Query Parameters:
        - category_id: Skill category UUID (required)
        - verified_only: true/false (default: true)
        - min_proficiency: beginner/intermediate/advanced/expert (optional)
        - limit: Number of results (default: 50)
        
        Example:
        GET /volunteer-search/by_skill_category/?category_id=uuid&verified_only=true
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        verified_only = request.query_params.get('verified_only', 'true').lower() == 'true'
        min_proficiency = request.query_params.get('min_proficiency', None)
        limit = int(request.query_params.get('limit', 50))
        
        try:
            results = VolunteerSearchService.search_volunteers_by_category(
                category_id=category_id,
                verified_only=verified_only,
                min_proficiency_level=min_proficiency,
                limit=limit
            )
            
            serializer = VolunteerSearchResultSerializer(results, many=True)
            return Response({
                'count': len(results),
                'category_id': category_id,
                'search_criteria': {
                    'verified_only': verified_only,
                    'min_proficiency': min_proficiency,
                },
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )