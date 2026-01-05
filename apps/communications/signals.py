from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.missions.models import Mission
from apps.accounts.models import Participation
from .models import MessageGroup, GroupMember
from apps.core.constants import MissionStatus, ParticipationStatus, MemberRole

@receiver(post_save, sender=Mission)
def create_mission_chat_group(sender, instance, created, **kwargs):
    """
    Automatically create a chat group when a mission is published
    """
    if instance.status == MissionStatus.PUBLISHED and not hasattr(instance, 'chat_group'):
        # Create the message group
        group = MessageGroup.objects.create(mission=instance)
        
        # Add organization admin as group admin
        GroupMember.objects.create(
            group=group,
            user=instance.organization.user,
            role=MemberRole.ADMIN
        )

@receiver(post_save, sender=Participation)
def add_volunteer_to_chat_group(sender, instance, **kwargs):
    """
    Automatically add volunteer to mission chat group when participation is accepted
    Only add if group is not full
    """
    if instance.status == ParticipationStatus.ACCEPTED:
        try:
            group = instance.mission.chat_group
            
            # Check if group is not full before adding
            if not group.is_full:
                # Add volunteer as member if not already in group
                GroupMember.objects.get_or_create(
                    group=group,
                    user=instance.volunteer.user,
                    defaults={'role': MemberRole.MEMBER}
                )
        except MessageGroup.DoesNotExist:
            # Group doesn't exist yet
            pass

@receiver(post_save, sender=Participation)
def remove_volunteer_from_chat_group(sender, instance, **kwargs):
    """
    Remove volunteer from chat group if participation is rejected, cancelled, or completed
    """
    if instance.status in [ParticipationStatus.REJECTED, ParticipationStatus.CANCELLED, ParticipationStatus.COMPLETED]:
        try:
            group = instance.mission.chat_group
            # Remove volunteer from group
            GroupMember.objects.filter(
                group=group,
                user=instance.volunteer.user
            ).delete()
        except MessageGroup.DoesNotExist:
            pass