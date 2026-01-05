from rest_framework import serializers
import re
from apps.accounts.models import User
from apps.core.constants import UserType


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'user_type',
            'user_type_display',
            'avatar',
            'profile_picture_url',
            'is_verified',
            'date_joined',
            'rating_display',
            'average_rating',
        ]
        read_only_fields = [
            'id',
            'email',
            'user_type',
            'is_verified',
            'date_joined',
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_picture_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    has_volunteer_profile = serializers.SerializerMethodField()
    has_organization_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'user_type',
            'user_type_display',
            'phone_number',
            'avatar',
            'profile_picture_url',
            'is_verified',
            'is_active',
            'date_joined',
            'last_login',
            'total_rating',
            'rating_count',
            'average_rating',
            'rating_display',
            'has_volunteer_profile',
            'has_organization_profile',
        ]
        read_only_fields = [
            'id',
            'email',
            'username',
            'user_type',
            'is_verified',
            'is_active',
            'date_joined',
            'last_login',
            'total_rating',
            'rating_count',
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_picture_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None
    
    def get_has_volunteer_profile(self, obj):
        return hasattr(obj, 'volunteer_profile') and obj.volunteer_profile is not None
    
    def get_has_organization_profile(self, obj):
        return hasattr(obj, 'organization_profile') and obj.organization_profile is not None


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'avatar',
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not value:
            return value
        
        cleaned = value.replace(' ', '').replace('-', '')
        
        pattern = r'^(\+213|0)[5-7][0-9]{8}$'
        
        if not re.match(pattern, cleaned):
            raise serializers.ValidationError(
                'Enter a valid Algerian phone number. Format: +213XXXXXXXXX or 0XXXXXXXXX'
            )
        
        return value
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance