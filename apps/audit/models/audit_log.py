import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.core.models import BaseModel
from apps.accounts.models import User

class AuditLog(BaseModel):
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        STATUS_CHANGE = 'status_change', 'Status Change'
        VERIFICATION = 'verification', 'Verification'
        VALIDATION = 'validation', 'Validation'
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()  # Changed to UUID to match our models
    content_object = GenericForeignKey('content_type', 'object_id')
    
    previous_state = models.JSONField(blank=True, null=True)
    new_state = models.JSONField(blank=True, null=True)
    changed_fields = models.JSONField(default=list, blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email if self.user else 'System'} - {self.action_type}"