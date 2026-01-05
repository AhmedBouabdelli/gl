import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import NotificationType, NotificationChannel

class Notification(BaseModel):
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50, 
        choices=NotificationType.CHOICES
    )
    channel = models.CharField(
        max_length=20, 
        choices=NotificationChannel.CHOICES, 
        default=NotificationChannel.IN_APP
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"