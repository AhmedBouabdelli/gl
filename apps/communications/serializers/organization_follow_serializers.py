from rest_framework import serializers
from .models import OrganizationFollow
from apps.accounts.models import VolunteerProfile, OrganizationProfile


class OrganizationMinimalSerializer(serializers.ModelSerializer):
    """Minimal organization info for follow lists"""
    organization_name = serializers.CharField()
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = OrganizationProfile
        fields = [
            'id',
            'organization_name',
            'email',
            'phone',
            'wilaya',
            'organization_type',
            'logo',
            'description'
        ]
        read_only_fields = ['id']


class VolunteerMinimalSerializer(serializers.ModelSerializer):
    """Minimal volunteer info for follower lists"""
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = VolunteerProfile
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'wilaya',
            'profile_picture'
        ]
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        if hasattr(obj, 'user'):
            return obj.user.get_full_name()
        return ""


class OrganizationFollowListSerializer(serializers.ModelSerializer):
    """List of organizations a volunteer is following"""
    organization = OrganizationMinimalSerializer(read_only=True)
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    mission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganizationFollow
        fields = [
            'id',
            'organization',
            'followed_at',
            'notify_on_new_mission',
            'notify_on_updates',
            'mission_count'
        ]
        read_only_fields = ['id', 'followed_at']
    
    def get_mission_count(self, obj):
        """Get active mission count for the organization"""
        if hasattr(obj.organization, 'missions'):
            return obj.organization.missions.filter(status='published').count()
        return 0


class OrganizationFollowerListSerializer(serializers.ModelSerializer):
    """List of volunteers following an organization"""
    volunteer = VolunteerMinimalSerializer(read_only=True)
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = OrganizationFollow
        fields = [
            'id',
            'volunteer',
            'followed_at',
            'notify_on_new_mission',
            'notify_on_updates'
        ]
        read_only_fields = ['id', 'followed_at']


class OrganizationFollowCreateSerializer(serializers.Serializer):
    """Create a follow relationship"""
    organization_id = serializers.UUIDField(required=True)
    notify_on_new_mission = serializers.BooleanField(default=True)
    notify_on_updates = serializers.BooleanField(default=True)
    
    def validate_organization_id(self, value):
        """Check if organization exists"""
        try:
            OrganizationProfile.objects.get(id=value)
        except OrganizationProfile.DoesNotExist:
            raise serializers.ValidationError("Organization not found")
        return value


class OrganizationFollowUpdateSerializer(serializers.Serializer):
    """Update notification preferences"""
    notify_on_new_mission = serializers.BooleanField(required=False)
    notify_on_updates = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Ensure at least one field is provided"""
        if not attrs:
            raise serializers.ValidationError(
                "At least one notification preference must be provided"
            )
        return attrs


class FeedMissionSerializer(serializers.Serializer):
    """Serializer for feed missions with organization info"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    mission_type = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    location = serializers.CharField()
    wilaya = serializers.CharField()
    volunteers_needed = serializers.IntegerField()
    volunteers_registered = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    # Organization info
    organization_id = serializers.UUIDField()
    organization_name = serializers.CharField()
    organization_logo = serializers.ImageField(allow_null=True)
    
    # Follow info
    followed_at = serializers.DateTimeField()
    notifications_enabled = serializers.BooleanField()