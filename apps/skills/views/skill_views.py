"""
Skill ViewSet
Handles API endpoints for skill management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Skill
from ..services import SkillService
from ..serializers import (
    SkillListSerializer,
    SkillDetailSerializer,
    SkillCreateSerializer,
    SkillUpdateSerializer,
    SkillStatisticsSerializer,
)
from apps.core.permissions import get_skill_permissions


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skills
    
    Permissions:
    - Read operations (list, retrieve, search, etc.): Public access
    - Write operations (create, update, delete): Admin only
    """
    queryset = Skill.objects.all()
    serializer_class = SkillListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return SkillCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SkillUpdateSerializer
        elif self.action == 'retrieve':
            return SkillDetailSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        return get_skill_permissions(self.action)
    
    def get_queryset(self):
        """
        Return skills with filtering
        """
        queryset = super().get_queryset()
        
        # Filter by verification requirement
        verification_required = self.request.query_params.get('verification_required')
        if verification_required is not None:
            verification_required = verification_required.lower() == 'true'
            if verification_required:
                queryset = queryset.exclude(verification_requirement='none')
            else:
                queryset = queryset.filter(verification_requirement='none')
        
        return queryset.select_related('category')
    
    def list(self, request, *args, **kwargs):
        """
        List skills with enhanced filtering
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get popular skills if requested
        popular = request.query_params.get('popular', '').lower() == 'true'
        if popular:
            limit = int(request.query_params.get('limit', 10))
            skills = SkillService.get_popular_skills(limit)
            serializer = self.get_serializer(skills, many=True)
            return Response(serializer.data)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get most popular skills (by volunteer count)
        """
        try:
            limit = int(request.query_params.get('limit', 10))
            popular_skills = SkillService.get_popular_skills(limit)
            serializer = self.get_serializer(popular_skills, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, id=None):
        """
        Get statistics for a specific skill
        """
        try:
            stats = SkillService.get_skill_statistics(id)
            serializer = SkillStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, id=None):
        """
        Activate a skill (Admin only)
        """
        try:
            skill = SkillService.activate_skill(id)
            serializer = SkillDetailSerializer(skill)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, id=None):
        """
        Deactivate a skill (Admin only)
        """
        try:
            skill = SkillService.deactivate_skill(id)
            serializer = SkillDetailSerializer(skill)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search skills by name or description
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category_id = request.query_params.get('category_id')
        
        try:
            results = SkillService.search_skills(query, category_id)
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get skills by category
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            skills = SkillService.get_skills_by_category(category_id)
            serializer = self.get_serializer(skills, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new skill (Admin only)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            skill = SkillService.create_skill(
                name=serializer.validated_data['name'],
                category_id=str(serializer.validated_data['category'].id),
                description=serializer.validated_data.get('description'),
                verification_requirement=serializer.validated_data.get('verification_requirement'),
                is_active=serializer.validated_data.get('is_active', True)
            )
            
            response_serializer = SkillDetailSerializer(skill)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update a skill (Admin only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            skill = SkillService.update_skill(
                skill_id=str(instance.id),
                name=serializer.validated_data.get('name'),
                category_id=str(serializer.validated_data.get('category').id) 
                if serializer.validated_data.get('category') else None,
                description=serializer.validated_data.get('description'),
                verification_requirement=serializer.validated_data.get('verification_requirement'),
                is_active=serializer.validated_data.get('is_active')
            )
            
            response_serializer = SkillDetailSerializer(skill)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a skill (Admin only)
        """
        instance = self.get_object()
        
        # Check if force option is provided
        force = request.query_params.get('force', '').lower() == 'true'
        
        try:
            result = SkillService.delete_skill(
                skill_id=str(instance.id),
                force=force
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )