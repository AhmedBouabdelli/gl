from .base import BaseService
from apps.accounts.models import VolunteerProfile


class VolunteerProfileService(BaseService):
    """Handle volunteer profile operations"""

    BADGE_LEVELS = {
        0: {'level': 'Bronze', 'min_hours': 0, 'max_hours': 50},
        1: {'level': 'Silver', 'min_hours': 50, 'max_hours': 100},
        2: {'level': 'Gold', 'min_hours': 100, 'max_hours': 200},
        3: {'level': 'Platinum', 'min_hours': 200, 'max_hours': float('inf')},
    }

    @staticmethod
    def create_volunteer_profile(user, bio='', hours_per_week=0):
        """Create volunteer profile"""
        profile = VolunteerProfile.objects.create(
            user=user,
            bio=bio,
            hours_per_week=hours_per_week,
            total_hours=0,
            completed_missions=0
        )
        VolunteerProfileService.log_info(f'Volunteer profile created: {user.email}')
        return profile

    @staticmethod
    def update_volunteer_profile(profile, **kwargs):
        """Update volunteer profile"""
        allowed_fields = ['bio', 'hours_per_week', 'skills', 'availability']

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)

        profile.save()
        return profile

    @staticmethod
    def add_volunteer_hours(profile, hours):
        """Add hours to volunteer profile"""
        if hours < 0:
            raise ValueError('Hours cannot be negative')
        profile.total_hours += hours
        profile.save()
        return profile

    @staticmethod
    def get_volunteer_badge(profile):
        """Calculate volunteer badge level"""
        total_hours = profile.total_hours
        current_badge = {'level': 'Bronze', 'hours': 0}
        next_badge = None

        for idx, badge in VolunteerProfileService.BADGE_LEVELS.items():
            if badge['min_hours'] <= total_hours < badge['max_hours']:
                current_badge = {'level': badge['level'], 'hours': total_hours}

                if idx < len(VolunteerProfileService.BADGE_LEVELS) - 1:
                    next_level = VolunteerProfileService.BADGE_LEVELS[idx + 1]
                    next_badge = {
                        'level': next_level['level'],
                        'target_hours': next_level['min_hours'],
                        'progress': total_hours
                    }
                break

        return {'current': current_badge, 'next': next_badge}

    @staticmethod
    def get_volunteer_statistics(profile):
        """Get comprehensive volunteer statistics"""
        return {
            'total_hours': profile.total_hours,
            'completed_missions': profile.completed_missions,
            'hours_per_week': profile.hours_per_week,
            'bio': profile.bio,
            'joined_date': profile.created_at.isoformat() if profile.created_at else None,
        }
