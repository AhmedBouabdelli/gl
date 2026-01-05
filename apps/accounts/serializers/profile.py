from rest_framework import serializers
import re

from apps.accounts.models import (
    VolunteerProfile,
    OrganizationProfile,
    Address
)
from apps.accounts.serializers.user import UserSerializer
from apps.core.constants import AvailabilityType, OrganizationType


VALID_WILAYAS = [
    'Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa',
    'Biskra', 'Béchar', 'Blida', 'Bouira', 'Tamanrasset', 'Tébessa',
    'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger', 'Djelfa', 'Jijel',
    'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma',
    'Constantine', 'Médéa', 'Mostaganem', 'M\'Sila', 'Mascara', 'Ouargla',
    'Oran', 'El Bayadh', 'Illizi', 'Bordj Bou Arréridj', 'Boumerdès',
    'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued', 'Khenchela', 'Souk Ahras',
    'Tipaza', 'Mila', 'Aïn Defla', 'Naâma', 'Aïn Témouchent', 'Ghardaïa',
    'Relizane', 'Timimoun', 'Bordj Badji Mokhtar', 'Ouled Djellal',
    'Béni Abbès', 'In Salah', 'In Guezzam', 'Touggourt', 'Djanet',
    'El M\'Ghair', 'El Meniaa'
]


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = [
            'id',
            'address_line_1',
            'address_line_2',
            'city',
            'wilaya',
            'country',
            'latitude',
            'longitude',
            'full_address',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_address(self, obj):
        return str(obj)
    
    def validate_wilaya(self, value):
        if value and value not in VALID_WILAYAS:
            raise serializers.ValidationError(
            )
        return value
    
    def validate(self, attrs):
        attrs['country'] = 'Algeria'
        return attrs


class VolunteerProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    availability_display = serializers.CharField(
        source='get_availability_display',
        read_only=True
    )
    skills = serializers.SerializerMethodField()
    verified_skills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VolunteerProfile
        fields = [
            'id',
            'user',
            'bio',
            'availability',
            'availability_display',
            'hours_per_week',
            'address',
            'willing_to_travel',
            'max_travel_distance_km',
            'skills',
            'verified_skills_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_skills(self, obj):

        try:
            from apps.skills.models import VolunteerSkill
            from apps.core.constants import SkillVerificationStatus
            
            volunteer_skills = VolunteerSkill.objects.filter(
                volunteer=obj
            ).select_related('skill')
            
            return [
                {
                    'id': vs.skill.id,
                    'name': vs.skill.name,
                    'verification_status': vs.verification_status,
                    'is_verified': vs.verification_status == SkillVerificationStatus.VERIFIED,
                }
                for vs in volunteer_skills
            ]
        except ImportError:
            return []
    
    def get_verified_skills_count(self, obj):
        try:
            from apps.skills.models import VolunteerSkill
            from apps.core.constants import SkillVerificationStatus
            
            return VolunteerSkill.objects.filter(
                volunteer=obj,
                verification_status=SkillVerificationStatus.VERIFIED
            ).count()
        except ImportError:
            return 0


class VolunteerProfileUpdateSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    
    class Meta:
        model = VolunteerProfile
        fields = [
            'bio',
            'availability',
            'hours_per_week',
            'address',
            'willing_to_travel',
            'max_travel_distance_km',
        ]
    
    def validate_bio(self, value):
        if value and len(value) < 100:
            raise serializers.ValidationError(
            )
        return value
    
    def validate_hours_per_week(self, value):
        if value and (value < 1 or value > 168):
            raise serializers.ValidationError(
            )
        return value
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if address_data:
            if instance.address:
                address_serializer = AddressSerializer(
                    instance.address,
                    data=address_data,
                    partial=True
                )
                if address_serializer.is_valid(raise_exception=True):
                    address_serializer.save()
            else:
                address_serializer = AddressSerializer(data=address_data)
                if address_serializer.is_valid(raise_exception=True):
                    address = address_serializer.save()
                    instance.address = address
        
        instance.save()
        return instance


class OrganizationProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    organization_type_display = serializers.CharField(
        source='get_organization_type_display',
        read_only=True
    )
    
    total_missions = serializers.SerializerMethodField()
    completed_missions = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganizationProfile
        fields = [
            'id',
            'user',
            'name',
            'description',
            'organization_type',
            'organization_type_display',
            'address',
            'website_url',
            'social_media_url',
            'total_missions',
            'completed_missions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_total_missions(self, obj):
        try:
            from apps.missions.models import Mission
            return Mission.objects.filter(organization=obj).count()
        except ImportError:
            return 0
    
    def get_completed_missions(self, obj):
        try:
            from apps.missions.models import Mission
            from apps.core.constants import MissionStatus
            return Mission.objects.filter(
                organization=obj,
                status=MissionStatus.COMPLETED
            ).count()
        except ImportError:
            return 0


class OrganizationProfileUpdateSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    
    class Meta:
        model = OrganizationProfile
        fields = [
            'name',
            'description',
            'organization_type',
            'address',
            'website_url',
            'social_media_url',
        ]
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                'Organization name must be at least 3 characters.'
            )
        return value
    
    def validate_description(self, value):
        if value and len(value) < 50:
            raise serializers.ValidationError(
            )
        return value
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if address_data:
            if instance.address:
                address_serializer = AddressSerializer(
                    instance.address,
                    data=address_data,
                    partial=True
                )
                if address_serializer.is_valid(raise_exception=True):
                    address_serializer.save()
            else:
                address_serializer = AddressSerializer(data=address_data)
                if address_serializer.is_valid(raise_exception=True):
                    address = address_serializer.save()
                    instance.address = address
        
        instance.save()
        return instance
