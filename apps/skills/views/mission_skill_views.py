"""
Mission Skill ViewSet
Handles API endpoints for mission skill requirement management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import MissionSkill
from ..services import MissionSkillService
from ..serializers import (
    MissionSkillListSerializer,
    MissionSkillDetailSerializer,
    MissionSkillCreateSerializer,
    MissionSkillUpdateSerializer,
    MissionSkillStatisticsSerializer,
    MissionSkillBulkCreateSerializer,
    MissionSkillValidationSerializer,
)
from apps.core.permissions import get_mission_skill_permissions


class MissionSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mission skill requirements
    
    Permissions:
    - Read operations (list, retrieve, required): Public access
    - Write operations (create, update, delete, bulk_add): Mission owners and admins
    - suggestions/validate_volunteer/statistics: Mission owners and admins
    """
    queryset = MissionSkill.objects.all()
    serializer_class = MissionSkillListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['requirement_level', 'is_verification_required']
    search_fields = ['skill__name', 'skill__description']
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return MissionSkillCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MissionSkillUpdateSerializer
        elif self.action == 'retrieve':
            return MissionSkillDetailSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        return get_mission_skill_permissions(self.action)
    
    def get_queryset(self):
        """
        Return mission skills for the specific mission
        """
        mission_id = self.request.query_params.get('mission_id')
        
        if mission_id:
            queryset = MissionSkill.objects.filter(
                mission_id=mission_id
            ).select_related('skill', 'skill__category')
        else:
            queryset = MissionSkill.objects.all().select_related('skill', 'skill__category')
        
        # Apply additional filters
        requirement_level = self.request.query_params.get('requirement_level')
        if requirement_level:
            queryset = queryset.filter(requirement_level=requirement_level)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List mission skill requirements (Public access)
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get required only if requested
        required_only = request.query_params.get('required_only', '').lower() == 'true'
        if required_only:
            from apps.core.constants import RequirementLevel
            queryset = queryset.filter(
                requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics for mission skills (Mission owners and admins only)
        """
        mission_id = request.query_params.get('mission_id')
        
        if not mission_id:
            return Response(
                {'error': 'mission_id is required as query parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stats = MissionSkillService.get_mission_skill_statistics(mission_id)
            serializer = MissionSkillStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        """
        Bulk add skills to mission (Mission owners and admins only)
        """
        mission_id = request.data.get('mission_id')
        
        if not mission_id:
            return Response(
                {'error': 'mission_id is required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MissionSkillBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = MissionSkillService.bulk_add_skills_to_mission(
                mission_id=mission_id,
                skills_data=serializer.validated_data['skills']
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Get skill suggestions for mission (Mission owners and admins only)
        """
        mission_id = request.query_params.get('mission_id')
        
        if not mission_id:
            return Response(
                {'error': 'mission_id is required as query parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            limit = int(request.query_params.get('limit', 5))
            suggestions = MissionSkillService.suggest_skills_for_mission(mission_id, limit)
            
            # Use minimal serializer for suggestions
            from ..serializers import SkillMinimalSerializer
            serializer = SkillMinimalSerializer(suggestions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def validate_volunteer(self, request):
        """
        Validate if a volunteer meets mission skill requirements (Mission owners and admins only)
        """
        mission_id = request.data.get('mission_id')
        volunteer_id = request.data.get('volunteer_id')
        
        if not mission_id or not volunteer_id:
            return Response(
                {'error': 'mission_id and volunteer_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get volunteer's verified skills
        from ..services import VolunteerSkillService
        verified_skill_ids = VolunteerSkillService.get_verified_skill_ids(volunteer_id)
        
        try:
            validation_result = MissionSkillService.validate_volunteer_for_mission(
                volunteer_verified_skills=verified_skill_ids,
                mission_id=mission_id
            )
            
            serializer = MissionSkillValidationSerializer(validation_result)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def required(self, request):
        """
        Get only required skills for mission (Public access)
        """
        from apps.core.constants import RequirementLevel
        
        mission_id = request.query_params.get('mission_id')
        if mission_id:
            queryset = self.get_queryset().filter(
                mission_id=mission_id,
                requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
            )
        else:
            queryset = self.get_queryset().filter(
                requirement_level__in=[RequirementLevel.REQUIRED, RequirementLevel.CRITICAL]
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Add skill requirement to mission (Mission owners and admins only)
        """
        mission_id = request.data.get('mission_id')
        
        if not mission_id:
            return Response(
                {'error': 'mission_id is required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            mission_skill = MissionSkillService.add_skill_to_mission(
                mission_id=mission_id,
                skill_id=str(serializer.validated_data['skill_id']),
                requirement_level=serializer.validated_data.get('requirement_level'),
                is_verification_required=serializer.validated_data.get('is_verification_required', False),
                min_proficiency_level=serializer.validated_data.get('min_proficiency_level')
            )
            
            response_serializer = MissionSkillDetailSerializer(mission_skill)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update mission skill requirement (Mission owners and admins only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            mission_skill = MissionSkillService.update_mission_skill(
                mission_skill_id=str(instance.id),
                requirement_level=serializer.validated_data.get('requirement_level'),
                is_verification_required=serializer.validated_data.get('is_verification_required'),
                min_proficiency_level=serializer.validated_data.get('min_proficiency_level')
            )
            
            response_serializer = MissionSkillDetailSerializer(mission_skill)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove skill requirement from mission (Mission owners and admins only)
        """
        instance = self.get_object()
        
        try:
            result = MissionSkillService.remove_skill_from_mission(
                mission_skill_id=str(instance.id),
                mission_id=str(instance.mission_id)  # Use existing mission_id
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )