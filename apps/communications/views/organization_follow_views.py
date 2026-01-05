from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.communications.models import OrganizationFollow
from apps.communications.services import OrganizationFollowService
from apps.communications.serializers import (
    OrganizationFollowListSerializer,
    OrganizationFollowerListSerializer,
    OrganizationFollowCreateSerializer,
    OrganizationFollowUpdateSerializer,
    FeedMissionSerializer,
)
from apps.core.permissions import IsVolunteer, IsOrganization


class OrganizationFollowViewSet(viewsets.ViewSet):
    """
    ViewSet for managing organization follows
    
    Endpoints:
    - POST /api/communications/follows/follow/ - Follow an organization [Volunteer]
    - DELETE /api/communications/follows/{org_id}/unfollow/ - Unfollow [Volunteer]
    - GET /api/communications/follows/my_following/ - List organizations I follow [Volunteer]
    - GET /api/communications/follows/my_followers/ - List my followers [Organization]
    - GET /api/communications/follows/feed/ - Get missions feed [Volunteer]
    - PATCH /api/communications/follows/{org_id}/notifications/ - Update notifications [Volunteer]
    - GET /api/communications/follows/{org_id}/check/ - Check if following [Volunteer]
    - GET /api/communications/follows/{org_id}/stats/ - Get stats [Public]
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsVolunteer])
    def follow(self, request):
        """
        Follow an organization [Volunteer only]
        
        POST /api/communications/follows/follow/
        
        Body:
        {
            "organization_id": "uuid",
            "notify_on_new_mission": true,
            "notify_on_updates": true
        }
        """
        serializer = OrganizationFollowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            follow = OrganizationFollowService.follow_organization(
                volunteer_id=str(request.user.volunteer_profile.id),
                organization_id=str(serializer.validated_data['organization_id']),
                notify_missions=serializer.validated_data.get('notify_on_new_mission', True),
                notify_updates=serializer.validated_data.get('notify_on_updates', True)
            )
            
            response_serializer = OrganizationFollowListSerializer(follow)
            return Response(
                {
                    'message': 'Successfully followed organization',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred while following the organization'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsVolunteer])
    def unfollow(self, request, pk=None):
        """
        Unfollow an organization [Volunteer only]
        
        DELETE /api/communications/follows/{organization_id}/unfollow/
        
        pk = organization_id (UUID)
        """
        try:
            result = OrganizationFollowService.unfollow_organization(
                volunteer_id=str(request.user.volunteer_profile.id),
                organization_id=pk
            )
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred while unfollowing the organization'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsVolunteer])
    def my_following(self, request):
        """
        Get list of organizations I'm following [Volunteer only]
        
        GET /api/communications/follows/my_following/?limit=50
        
        Query params:
        - limit: Max results (default 50, max 100)
        """
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        try:
            follows = OrganizationFollowService.get_volunteer_following(
                volunteer_id=str(request.user.volunteer_profile.id),
                limit=limit
            )
            
            serializer = OrganizationFollowListSerializer(follows, many=True)
            return Response({
                'count': follows.count() if hasattr(follows, 'count') else len(follows),
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': 'An error occurred while fetching following list'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOrganization])
    def my_followers(self, request):
        """
        Get list of volunteers following my organization [Organization only]
        
        GET /api/communications/follows/my_followers/?limit=100
        
        Query params:
        - limit: Max results (default 100, max 200)
        """
        limit = min(int(request.query_params.get('limit', 100)), 200)
        
        try:
            followers = OrganizationFollowService.get_organization_followers(
                organization_id=str(request.user.organization_profile.id),
                limit=limit
            )
            
            serializer = OrganizationFollowerListSerializer(followers, many=True)
            return Response({
                'count': followers.count() if hasattr(followers, 'count') else len(followers),
                'follower_count': OrganizationFollowService.get_follower_count(
                    str(request.user.organization_profile.id)
                ),
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': 'An error occurred while fetching followers list'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsVolunteer])
    def feed(self, request):
        """
        Get missions from organizations I follow [Volunteer only]
        This is the main "feed" endpoint
        
        GET /api/communications/follows/feed/?days=30&limit=50
        
        Query params:
        - days: Look back N days (default 30, max 90)
        - limit: Max missions (default 50, max 100)
        """
        days = min(int(request.query_params.get('days', 30)), 90)
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        try:
            # Get missions with follow info
            feed_data = OrganizationFollowService.get_feed_missions_with_follow_info(
                volunteer_id=str(request.user.volunteer_profile.id),
                days=days,
                limit=limit
            )
            
            serializer = FeedMissionSerializer(feed_data, many=True)
            return Response({
                'count': len(feed_data),
                'days': days,
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': 'An error occurred while fetching feed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsVolunteer])
    def notifications(self, request, pk=None):
        """
        Update notification preferences for an organization [Volunteer only]
        
        PATCH /api/communications/follows/{organization_id}/notifications/
        
        pk = organization_id (UUID)
        
        Body:
        {
            "notify_on_new_mission": true,
            "notify_on_updates": false
        }
        """
        serializer = OrganizationFollowUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            follow = OrganizationFollowService.update_notification_preferences(
                volunteer_id=str(request.user.volunteer_profile.id),
                organization_id=pk,
                notify_missions=serializer.validated_data.get('notify_on_new_mission'),
                notify_updates=serializer.validated_data.get('notify_on_updates')
            )
            
            response_serializer = OrganizationFollowListSerializer(follow)
            return Response({
                'message': 'Notification preferences updated successfully',
                'data': response_serializer.data
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred while updating preferences'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsVolunteer])
    def check(self, request, pk=None):
        """
        Check if I'm following an organization [Volunteer only]
        
        GET /api/communications/follows/{organization_id}/check/
        
        pk = organization_id (UUID)
        """
        try:
            is_following = OrganizationFollowService.is_following(
                volunteer_id=str(request.user.volunteer_profile.id),
                organization_id=pk
            )
            
            return Response({
                'is_following': is_following,
                'organization_id': pk
            })
        except Exception as e:
            return Response(
                {'error': 'An error occurred while checking follow status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        """
        Get follow statistics for an organization [Authenticated users]
        
        GET /api/communications/follows/{organization_id}/stats/
        
        pk = organization_id (UUID)
        """
        try:
            follower_count = OrganizationFollowService.get_follower_count(pk)
            
            return Response({
                'organization_id': pk,
                'follower_count': follower_count
            })
        except Exception as e:
            return Response(
                {'error': 'An error occurred while fetching stats'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )