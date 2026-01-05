from .base import BaseService
from apps.accounts.models import OrganizationProfile


class OrganizationProfileService(BaseService):
    """Handle organization profile operations"""

    @staticmethod
    def create_organization_profile(user, name='', description='', organization_type='ngo'):
        """Create organization profile"""
        profile = OrganizationProfile.objects.create(
            user=user,
            name=name,
            description=description,
            organization_type=organization_type,
            total_missions=0,
            completed_missions=0,
            active_volunteers=0
        )
        return profile

    @staticmethod
    def update_organization_profile(profile, **kwargs):
        """Update organization profile"""
        allowed_fields = ['name', 'description', 'organization_type', 'logo', 'website']

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)

        profile.save()
        return profile

    @staticmethod
    def get_organization_statistics(profile):
        """Get organization statistics"""
        return {
            'total_missions': profile.total_missions,
            'completed_missions': profile.completed_missions,
            'active_volunteers': profile.active_volunteers,
            'organization_type': profile.organization_type,
            'name': profile.name,
            'description': profile.description,
            'joined_date': profile.created_at.isoformat() if profile.created_at else None,
        }
