from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction
from apps.missions.models import Participation
from apps.accounts.models import User
from apps.core.constants import ParticipationStatus, UserType

class RatingService:
    
    @staticmethod
    @transaction.atomic
    def volunteer_rates_organization(participation, rating):
        """Volunteer rates the organization and update organization user's rating"""
        if participation.status != ParticipationStatus.COMPLETED:
            raise ValidationError("Can only rate after participation is completed")
        
        # Update participation
        participation.volunteer_rating = rating
        participation.save()
        
        # Update organization user's rating
        organization_user = participation.mission.organization.user
        RatingService._update_user_rating(organization_user)
        
        return participation
    
    @staticmethod
    @transaction.atomic
    def organization_rates_volunteer(participation, rating):
        """Organization rates the volunteer and update volunteer user's rating"""
        if participation.status != ParticipationStatus.COMPLETED:
            raise ValidationError("Can only rate after participation is completed")
        
        # Update participation
        participation.organization_rating = rating
        participation.save()
        
        # Update volunteer user's rating
        volunteer_user = participation.volunteer.user
        RatingService._update_user_rating(volunteer_user)
        
        return participation
    
    @staticmethod
    def _update_user_rating(user):
        """Recalculate user's average rating based on their user_type"""
        from django.db.models import Avg, Count
        
        if user.user_type == UserType.VOLUNTEER:
            # Volunteer rating = average of organization_rating
            rating_stats = Participation.objects.filter(
                volunteer__user=user,
                organization_rating__isnull=False,
                status=ParticipationStatus.COMPLETED
            ).aggregate(
                avg_rating=Avg('organization_rating'),
                rating_count=Count('id')
            )
        elif user.user_type == UserType.ORGANIZATION:
            # Organization rating = average of volunteer_rating
            rating_stats = Participation.objects.filter(
                mission__organization__user=user,
                volunteer_rating__isnull=False,
                status=ParticipationStatus.COMPLETED
            ).aggregate(
                avg_rating=Avg('volunteer_rating'),
                rating_count=Count('id')
            )
        else:
            return  # Admins don't get rated
        
        user.total_rating = rating_stats['avg_rating'] or 0.0
        user.rating_count = rating_stats['rating_count'] or 0
        user.last_rating_update = timezone.now()
        user.save()