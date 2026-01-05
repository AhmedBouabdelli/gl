from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from apps.communications.models import OrganizationFollow
from apps.accounts.models import VolunteerProfile, OrganizationProfile


class OrganizationFollowService:
    """Service layer for organization follow operations"""
    
    @staticmethod
    def follow_organization(volunteer_id, organization_id, notify_missions=True, notify_updates=True):
        """
        Follow an organization
        
        Args:
            volunteer_id: UUID of the volunteer
            organization_id: UUID of the organization
            notify_missions: Enable mission notifications
            notify_updates: Enable update notifications
            
        Returns:
            OrganizationFollow object
            
        Raises:
            ValueError: If volunteer or organization not found
            IntegrityError: If already following
        """
        volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
        organization = get_object_or_404(OrganizationProfile, id=organization_id)
        
        # Check if volunteer is trying to follow their own organization
        if volunteer.user == organization.user:
            raise ValueError("Cannot follow your own organization")
        
        try:
            follow = OrganizationFollow.objects.create(
                volunteer=volunteer,
                organization=organization,
                notify_on_new_mission=notify_missions,
                notify_on_updates=notify_updates
            )
            return follow
        except IntegrityError:
            raise ValueError("Already following this organization")
    
    @staticmethod
    def unfollow_organization(volunteer_id, organization_id):
        """
        Unfollow an organization
        
        Args:
            volunteer_id: UUID of the volunteer
            organization_id: UUID of the organization
            
        Returns:
            dict with success message
            
        Raises:
            ValueError: If not following
        """
        volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
        organization = get_object_or_404(OrganizationProfile, id=organization_id)
        
        deleted_count, _ = OrganizationFollow.objects.filter(
            volunteer=volunteer,
            organization=organization
        ).delete()
        
        if deleted_count == 0:
            raise ValueError("Not following this organization")
        
        return {
            'message': 'Successfully unfollowed organization',
            'organization_id': str(organization_id)
        }
    
    @staticmethod
    def get_volunteer_following(volunteer_id, limit=50):
        """
        Get list of organizations a volunteer is following
        
        Args:
            volunteer_id: UUID of the volunteer
            limit: Maximum results to return
            
        Returns:
            QuerySet of OrganizationFollow objects
        """
        volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
        
        return OrganizationFollow.objects.filter(
            volunteer=volunteer
        ).select_related(
            'organization',
            'organization__user'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_organization_followers(organization_id, limit=100):
        """
        Get list of volunteers following an organization
        
        Args:
            organization_id: UUID of the organization
            limit: Maximum results to return
            
        Returns:
            QuerySet of OrganizationFollow objects
        """
        organization = get_object_or_404(OrganizationProfile, id=organization_id)
        
        return OrganizationFollow.objects.filter(
            organization=organization
        ).select_related(
            'volunteer',
            'volunteer__user'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_follower_count(organization_id):
        """
        Get total follower count for an organization
        
        Args:
            organization_id: UUID of the organization
            
        Returns:
            int: Number of followers
        """
        return OrganizationFollow.objects.filter(
            organization_id=organization_id
        ).count()
    
    @staticmethod
    def is_following(volunteer_id, organization_id):
        """
        Check if a volunteer is following an organization
        
        Args:
            volunteer_id: UUID of the volunteer
            organization_id: UUID of the organization
            
        Returns:
            bool: True if following, False otherwise
        """
        return OrganizationFollow.objects.filter(
            volunteer_id=volunteer_id,
            organization_id=organization_id
        ).exists()
    
    @staticmethod
    def update_notification_preferences(volunteer_id, organization_id, notify_missions=None, notify_updates=None):
        """
        Update notification preferences for a follow relationship
        
        Args:
            volunteer_id: UUID of the volunteer
            organization_id: UUID of the organization
            notify_missions: Enable/disable mission notifications (optional)
            notify_updates: Enable/disable update notifications (optional)
            
        Returns:
            OrganizationFollow object
            
        Raises:
            ValueError: If not following
        """
        try:
            follow = OrganizationFollow.objects.get(
                volunteer_id=volunteer_id,
                organization_id=organization_id
            )
        except OrganizationFollow.DoesNotExist:
            raise ValueError("Not following this organization")
        
        if notify_missions is not None:
            follow.notify_on_new_mission = notify_missions
        
        if notify_updates is not None:
            follow.notify_on_updates = notify_updates
        
        follow.save()
        return follow
    
    @staticmethod
    def get_feed_missions_with_follow_info(volunteer_id, days=30, limit=50):
        """
        Get missions from organizations the volunteer follows
        
        Args:
            volunteer_id: UUID of the volunteer
            days: Look back N days
            limit: Maximum missions to return
            
        Returns:
            list: Mission data with organization and follow info
        """
        volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
        
        # Get organizations the volunteer follows
        follows = OrganizationFollow.objects.filter(
            volunteer=volunteer
        ).select_related('organization')
        
        if not follows.exists():
            return []
        
        # Calculate date threshold
        date_threshold = timezone.now() - timedelta(days=days)
        
        # Get missions from followed organizations
        from apps.missions.models import Mission
        
        missions = Mission.objects.filter(
            organization__in=[f.organization for f in follows],
            created_at__gte=date_threshold,
            status='published'
        ).select_related(
            'organization'
        ).order_by('-created_at')[:limit]
        
        # Create follow lookup
        follow_lookup = {f.organization_id: f for f in follows}
        
        # Build feed data
        feed_data = []
        for mission in missions:
            follow = follow_lookup.get(mission.organization_id)
            feed_data.append({
                'id': mission.id,
                'title': mission.title,
                'description': mission.description,
                'status': mission.status,
                'mission_type': mission.mission_type,
                'start_date': mission.start_date,
                'end_date': mission.end_date,
                'location': mission.location,
                'wilaya': mission.wilaya,
                'volunteers_needed': mission.volunteers_needed,
                'volunteers_registered': getattr(mission, 'volunteers_registered', 0),
                'created_at': mission.created_at,
                'organization_id': mission.organization.id,
                'organization_name': mission.organization.organization_name,
                'organization_logo': mission.organization.logo,
                'followed_at': follow.created_at if follow else None,
                'notifications_enabled': follow.notify_on_new_mission if follow else False
            })
        
        return feed_data