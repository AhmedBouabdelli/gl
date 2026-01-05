"""
Skill Category ViewSet
Handles API endpoints for skill category management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import SkillCategory
from ..services import SkillCategoryService
from ..serializers import (
    SkillCategoryListSerializer,
    SkillCategoryDetailSerializer,
    SkillCategoryCreateSerializer,
    SkillCategoryUpdateSerializer,
    SkillCategoryTreeSerializer,
    SkillCategoryStatisticsSerializer,
)
from apps.core.permissions import get_skill_category_permissions


class SkillCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skill categories
    
    Permissions:
    - Read operations (list, retrieve, tree, etc.): Public access
    - Write operations (create, update, delete): Admin only
    """
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategoryListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return SkillCategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SkillCategoryUpdateSerializer
        elif self.action == 'retrieve':
            return SkillCategoryDetailSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        return get_skill_category_permissions(self.action)
    
    def get_queryset(self):
        """
        Return categories, optionally filtered
        """
        queryset = super().get_queryset()
        
        # Apply filters
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            if parent_id == 'null':
                queryset = queryset.filter(parent_category__isnull=True)
            else:
                queryset = queryset.filter(parent_category_id=parent_id)
        
        return queryset.select_related('parent_category')
    
    def list(self, request, *args, **kwargs):
        """
        List categories with enhanced filtering
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get root categories if requested
        root_only = request.query_params.get('root_only', '').lower() == 'true'
        if root_only:
            queryset = queryset.filter(parent_category__isnull=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get hierarchical category tree
        """
        try:
            tree_data = SkillCategoryService.get_category_tree()
            serializer = SkillCategoryTreeSerializer(tree_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, id=None):
        """
        Get statistics for a specific category
        """
        try:
            stats = SkillCategoryService.get_category_statistics(id)
            serializer = SkillCategoryStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def path(self, request, id=None):
        """
        Get path from root to this category
        """
        try:
            category = self.get_object()
            path = SkillCategoryService.get_category_path(category)
            
            # Build path data
            path_data = []
            for i, cat in enumerate(path):
                path_data.append({
                    'id': str(cat.id),
                    'name': cat.name,
                    'level': i + 1
                })
            
            return Response(path_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def roots(self, request):
        """
        Get all root categories (no parent)
        """
        try:
            roots = SkillCategoryService.get_root_categories()
            serializer = SkillCategoryListSerializer(roots, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search categories by name or description
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            results = SkillCategoryService.search_categories(query)
            serializer = SkillCategoryListSerializer(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new skill category (Admin only)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            category = SkillCategoryService.create_category(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description'),
                parent_category_id=str(serializer.validated_data.get('parent_category').id) 
                if serializer.validated_data.get('parent_category') else None
            )
            
            response_serializer = SkillCategoryDetailSerializer(category)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update a skill category (Admin only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            category = SkillCategoryService.update_category(
                category_id=str(instance.id),
                name=serializer.validated_data.get('name'),
                description=serializer.validated_data.get('description'),
                parent_category_id=str(serializer.validated_data.get('parent_category').id) 
                if serializer.validated_data.get('parent_category') else None
            )
            
            response_serializer = SkillCategoryDetailSerializer(category)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a skill category (Admin only)
        """
        instance = self.get_object()
        
        # Check if reassign option is provided
        reassign = request.query_params.get('reassign', '').lower() == 'true'
        
        try:
            result = SkillCategoryService.delete_category(
                category_id=str(instance.id),
                reassign_to_parent=reassign
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )