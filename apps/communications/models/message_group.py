import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import BaseModel
from apps.core.constants import ChatGroupStatus, MemberRole

class MessageGroup(BaseModel):
    """
    Chat group automatically created when a mission is published
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.OneToOneField(
        'missions.Mission', 
        on_delete=models.CASCADE, 
        related_name='chat_group'
    )
    status = models.CharField(
        max_length=20, 
        choices=ChatGroupStatus.CHOICES, 
        default=ChatGroupStatus.ACTIVE
    )
    
    class Meta:
        db_table = 'message_groups'
        indexes = [
            models.Index(fields=['mission', 'status']),
        ]

    def __str__(self):
        return f"Chat: {self.mission.title}"

    @property
    def name(self):
        """Auto-generated name from mission title"""
        return f"{self.mission.title} - Chat"

    @property
    def member_count(self):
        return self.group_members.filter(is_active=True).count()

    @property
    def max_members(self):
        """Max members equals volunteers needed in the mission"""
        return self.mission.volunteers_needed

    @property
    def organization_admin(self):
        """Get the organization admin user"""
        return self.mission.organization.user

    @property
    def is_full(self):
        """Check if group has reached maximum capacity"""
        return self.member_count >= self.max_members

class GroupMember(BaseModel):
    """
    Members of a message group with roles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        MessageGroup, 
        on_delete=models.CASCADE, 
        related_name='group_members'
    )
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='group_memberships'
    )
    role = models.CharField(
        max_length=20, 
        choices=MemberRole.CHOICES, 
        default=MemberRole.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'group_members'
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'user'], 
                name='unique_group_member'
            ),
        ]
        indexes = [
            models.Index(fields=['group', 'role']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.group.mission.title} ({self.role})"

    @property
    def is_admin(self):
        return self.role == MemberRole.ADMIN

    @property
    def is_moderator(self):
        return self.role in [MemberRole.ADMIN, MemberRole.MODERATOR]