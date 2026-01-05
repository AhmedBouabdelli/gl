from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import VolunteerSkill, VerificationRequest
from ..services import VolunteerSkillService, VerificationService
from ..serializers import (
    VolunteerSkillListSerializer,
    VolunteerSkillDetailSerializer,
    VolunteerSkillCreateSerializer,
    VolunteerSkillUpdateSerializer,
    VolunteerSkillVerifySerializer,
    VolunteerSkillStatisticsSerializer,
    VolunteerSkillBulkImportSerializer,
    SkillRequirementCheckSerializer,
    VerificationRequestSerializer,
    VerificationRequestCreateSerializer,
    VerificationRequestReviewSerializer,
)
from apps.core.permissions import get_volunteer_skill_permissions


class VolunteerSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing volunteer skills
    
    Permissions:
    - verify/review_verification/pending_verification_requests: Admin only
    - request_verification: Volunteer can request for own skills
    - verification_requests: Volunteer can view own verification requests
    - create/update/delete/bulk_import: Volunteer can manage own skills
    - list/retrieve/statistics/suggestions/check_requirements/verified: Volunteer sees own, admin sees all
    """
    queryset = VolunteerSkill.objects.all()
    serializer_class = VolunteerSkillListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['verification_status', 'is_primary', 'verification_requested']
    search_fields = ['skill__name', 'skill__description']
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return VolunteerSkillCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VolunteerSkillUpdateSerializer
        elif self.action == 'retrieve':
            return VolunteerSkillDetailSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        return get_volunteer_skill_permissions(self.action)
    
    def get_queryset(self):
        """
        Return volunteer skills based on user role
        """
        user = self.request.user
        
        # Admins can see all skills
        if user and user.is_staff:
            return VolunteerSkill.objects.select_related(
                'skill', 'skill__category', 'verified_by'
            ).all()
        
        # Volunteers can only see their own skills
        if user and hasattr(user, 'volunteer_profile'):
            return VolunteerSkill.objects.filter(
                volunteer=user.volunteer_profile
            ).select_related(
                'skill', 'skill__category', 'verified_by'
            ).all()
        
        # Default (should not happen with proper permissions)
        return VolunteerSkill.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        List volunteer skills
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by verification request status
        has_verification_request = request.query_params.get('has_verification_request')
        if has_verification_request:
            if has_verification_request.lower() == 'true':
                queryset = queryset.filter(verification_requested=True)
            elif has_verification_request.lower() == 'false':
                queryset = queryset.filter(verification_requested=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def request_verification(self, request, id=None):
        """
        Request verification for a volunteer skill (Volunteer only, for own skills)
        """
        instance = self.get_object()
        
        serializer = VerificationRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            verification_request = VerificationService.request_verification(
                volunteer_skill_id=str(instance.id),
                documents=serializer.validated_data.get('documents'),
                links=serializer.validated_data.get('links', []),
                notes=serializer.validated_data.get('notes', '')
            )
            
            response_serializer = VerificationRequestSerializer(verification_request)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def verification_requests(self, request, id=None):
        """
        Get verification requests for a volunteer skill (Volunteer can view own requests)
        """
        instance = self.get_object()
        
        try:
            requests = VerificationService.get_verification_requests_for_skill(
                volunteer_skill_id=str(instance.id)
            )
            
            response_serializer = VerificationRequestSerializer(requests, many=True)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pending_verification_requests(self, request):
        """
        Get all pending verification requests (Admin only)
        """
        try:
            requests = VerificationService.get_pending_verification_requests()
            
            page = self.paginate_queryset(requests)
            if page is not None:
                serializer = VerificationRequestSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = VerificationRequestSerializer(requests, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def review_verification(self, request, id=None):
        """
        Review a verification request (Admin only)
        """
        try:
            # Get the verification request ID from request data
            verification_request_id = request.data.get('verification_request_id')
            if not verification_request_id:
                return Response(
                    {'error': 'verification_request_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = VerificationRequestReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Use the authenticated admin user
            reviewer_id = str(request.user.id)
            
            reviewed_request = VerificationService.review_verification_request(
                verification_request_id=verification_request_id,
                reviewer_id=reviewer_id,
                review_status=serializer.validated_data['review_status'],
                review_notes=serializer.validated_data.get('review_notes', ''),
                admin_notes=serializer.validated_data.get('admin_notes', '')
            )
            
            response_serializer = VerificationRequestSerializer(reviewed_request)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get skill statistics for a volunteer (Volunteer sees own, Admin sees any)
        """
        volunteer_id = request.query_params.get('volunteer_id')
        user = request.user
        
        # If admin is viewing, they can specify any volunteer_id
        # If volunteer is viewing, they can only see their own stats
        if not user.is_staff:
            # Volunteer can only see their own stats
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only view your own statistics'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if not volunteer_id:
            return Response(
                {'error': 'volunteer_id is required as query parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stats = VolunteerSkillService.get_volunteer_skill_statistics(volunteer_id)
            serializer = VolunteerSkillStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Get skill suggestions for a volunteer (Volunteer sees own, Admin sees any)
        """
        volunteer_id = request.query_params.get('volunteer_id')
        user = request.user
        
        # If admin is viewing, they can specify any volunteer_id
        # If volunteer is viewing, they can only see their own suggestions
        if not user.is_staff:
            # Volunteer can only see their own suggestions
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only view your own skill suggestions'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if not volunteer_id:
            return Response(
                {'error': 'volunteer_id is required as query parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            limit = int(request.query_params.get('limit', 5))
            suggestions = VolunteerSkillService.suggest_skills_for_volunteer(volunteer_id, limit)
            
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
    def bulk_import(self, request):
        """
        Bulk import skills for volunteer (Volunteer only, for own skills)
        """
        serializer = VolunteerSkillBulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        volunteer_id = request.data.get('volunteer_id')
        user = request.user
        
        # Volunteer can only import skills for themselves
        if not user.is_staff:
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only import skills for yourself'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if not volunteer_id:
            return Response(
                {'error': 'volunteer_id is required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = VolunteerSkillService.bulk_import_skills(
                volunteer_id=volunteer_id,
                skills_data=serializer.validated_data['skills']
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, id=None):
        """
        Verify or reject a volunteer's skill (Admin only)
        """
        instance = self.get_object()
        
        serializer = VolunteerSkillVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use the authenticated admin user
            verifier_id = str(request.user.id)
            
            verified_skill = VolunteerSkillService.verify_skill(
                volunteer_skill_id=str(instance.id),
                verifier_user_id=verifier_id,
                verification_status=serializer.validated_data['verification_status'],
                verification_notes=serializer.validated_data.get('verification_notes', '')
            )
            
            response_serializer = VolunteerSkillDetailSerializer(verified_skill)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def check_requirements(self, request):
        """
        Check if volunteer has required skills for a mission (Volunteer sees own, Admin sees any)
        """
        required_skill_ids = request.data.get('required_skill_ids', [])
        volunteer_id = request.data.get('volunteer_id')
        user = request.user
        
        # If admin is checking, they can specify any volunteer_id
        # If volunteer is checking, they can only check their own requirements
        if not user.is_staff:
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only check your own skill requirements'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if not volunteer_id:
            return Response(
                {'error': 'volunteer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not required_skill_ids:
            return Response(
                {'error': 'required_skill_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validation_result = VolunteerSkillService.check_skill_requirements_for_mission(
                volunteer_id=volunteer_id,
                required_skill_ids=set(required_skill_ids)
            )
            
            serializer = SkillRequirementCheckSerializer(validation_result)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        """
        Get only verified skills (Volunteer sees own, Admin sees any)
        """
        from apps.core.constants import SkillVerificationStatus
        
        volunteer_id = request.query_params.get('volunteer_id')
        user = request.user
        
        # If admin is viewing, they can specify any volunteer_id
        # If volunteer is viewing, they can only see their own verified skills
        if not user.is_staff:
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only view your own verified skills'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        queryset = self.get_queryset().filter(
            verification_status=SkillVerificationStatus.VERIFIED
        )
        
        # Filter by volunteer_id if provided
        if volunteer_id:
            queryset = queryset.filter(volunteer_id=volunteer_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Add a skill to volunteer profile (Volunteer only, for own skills)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        volunteer_id = request.data.get('volunteer_id')
        user = request.user
        
        # Volunteer can only add skills to themselves
        if not user.is_staff:
            if hasattr(user, 'volunteer_profile'):
                volunteer_id = str(user.volunteer_profile.id)
            else:
                return Response(
                    {'error': 'You can only add skills to yourself'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if not volunteer_id:
            return Response(
                {'error': 'volunteer_id is required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            volunteer_skill = VolunteerSkillService.add_skill_to_volunteer(
                volunteer_id=volunteer_id,
                skill_id=str(serializer.validated_data['skill_id']),
                proficiency_level=serializer.validated_data.get('proficiency_level'),
                last_used_date=serializer.validated_data.get('last_used_date'),
                supporting_document=serializer.validated_data.get('supporting_document'),
                supporting_url=serializer.validated_data.get('supporting_url'),
                is_primary=serializer.validated_data.get('is_primary', False)
            )
            
            response_serializer = VolunteerSkillDetailSerializer(volunteer_skill)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update volunteer's skill (Volunteer only, for own skills)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            volunteer_skill = VolunteerSkillService.update_volunteer_skill(
                volunteer_skill_id=str(instance.id),
                volunteer_id=str(instance.volunteer_id),  # Use existing volunteer_id
                proficiency_level=serializer.validated_data.get('proficiency_level'),
                last_used_date=serializer.validated_data.get('last_used_date'),
                supporting_document=serializer.validated_data.get('supporting_document'),
                supporting_url=serializer.validated_data.get('supporting_url'),
                is_primary=serializer.validated_data.get('is_primary')
            )
            
            response_serializer = VolunteerSkillDetailSerializer(volunteer_skill)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove skill from volunteer profile (Volunteer only, for own skills)
        """
        instance = self.get_object()
        
        try:
            result = VolunteerSkillService.remove_skill_from_volunteer(
                volunteer_skill_id=str(instance.id),
                volunteer_id=str(instance.volunteer_id)  # Use existing volunteer_id
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )