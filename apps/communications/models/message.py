import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import MessageType

class Message(BaseModel):
    """
    Messages within a group chat - simplified without file attachments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        'communications.MessageGroup', 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    message_type = models.CharField(
        max_length=20, 
        choices=MessageType.CHOICES, 
        default=MessageType.TEXT
    )
    content = models.TextField()
    
    # Message status fields
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['group', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email} - {self.group.mission.title}"

    @property
    def reply_count(self):
        return self.replies.count()

class MessageReadReceipt(BaseModel):
    """
    Track which users have read which messages
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='message_read_receipts'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_read_receipts'
        constraints = [
            models.UniqueConstraint(
                fields=['message', 'user'], 
                name='unique_message_read'
            ),
        ]
        indexes = [
            models.Index(fields=['message', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.email} read message at {self.read_at}"