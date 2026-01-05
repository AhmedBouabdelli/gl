from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Full notification serializer"""
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_info',
            'notification_type',
            'channel',
            'title',
            'message',
            'data',
            'is_read',
            'read_at',
            'is_sent',
            'sent_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user', 'is_read', 'read_at', 'is_sent', 'sent_at', 'created_at', 'updated_at']
    
    def get_user_info(self, obj):
        return {
            'id': str(obj.user.id),
            'email': obj.user.email
        }


class NotificationListSerializer(serializers.ModelSerializer):
    """List serializer for notifications"""
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    class Meta:
        model = Notification
        fields = ['user', 'notification_type', 'channel', 'title', 'message', 'data']


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications"""
    class Meta:
        model = Notification
        fields = ['is_read']
    
    def update(self, instance, validated_data):
        instance.is_read = validated_data.get('is_read', instance.is_read)
        if instance.is_read and not instance.read_at:
            from django.utils import timezone
            instance.read_at = timezone.now()
        instance.save()
        return instance