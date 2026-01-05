from rest_framework import serializers
from ..models import VolunteerSkill, Skill, VerificationRequest
from apps.core.constants import SkillVerificationStatus, ProficiencyLevel


class SkillMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for skills in volunteer context"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    verification_requirement_display = serializers.CharField(
        source='get_verification_requirement_display',
        read_only=True
    )
    
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'category_name',
            'verification_requirement',
            'verification_requirement_display'
        ]
        read_only_fields = fields


class VolunteerSkillListSerializer(serializers.ModelSerializer):
    """Serializer for listing volunteer skills"""
    
    skill = SkillMinimalSerializer(read_only=True)
    proficiency_level_display = serializers.CharField(
        source='get_proficiency_level_display',
        read_only=True
    )
    verification_status_display = serializers.CharField(
        source='get_verification_status_display',
        read_only=True
    )
    verified_by_name = serializers.CharField(
        source='verified_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = VolunteerSkill
        fields = [
            'id',
            'skill',
            'proficiency_level',
            'proficiency_level_display',
            'verification_status',
            'verification_status_display',
            'verified_by_name',
            'verification_date',
            'verification_requested',
            'last_used_date',
            'is_primary',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'verification_status',
            'verified_by_name',
            'verification_date',
            'verification_requested',
            'created_at',
            'updated_at'
        ]


class VolunteerSkillDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for volunteer skills"""
    
    skill = SkillMinimalSerializer(read_only=True)
    proficiency_level_display = serializers.CharField(
        source='get_proficiency_level_display',
        read_only=True
    )
    verification_status_display = serializers.CharField(
        source='get_verification_status_display',
        read_only=True
    )
    verified_by_details = serializers.SerializerMethodField()
    verification_request_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VolunteerSkill
        fields = [
            'id',
            'skill',
            'proficiency_level',
            'proficiency_level_display',
            'verification_status',
            'verification_status_display',
            'verified_by_details',
            'verification_date',
            'verification_notes',
            'verification_requested',
            'verification_request_date',
            'verification_documents',
            'verification_links',
            'verification_request_info',
            'last_used_date',
            'supporting_document',
            'supporting_url',
            'is_primary',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'verification_status',
            'verified_by_details',
            'verification_date',
            'verification_notes',
            'verification_requested',
            'verification_request_date',
            'verification_documents',
            'verification_links',
            'verification_request_info',
            'created_at',
            'updated_at'
        ]
    
    def get_verified_by_details(self, obj):
        """Get verifier details"""
        if not obj.verified_by:
            return None
        
        return {
            'id': str(obj.verified_by.id),
            'name': obj.verified_by.get_full_name(),
            'email': obj.verified_by.email
        }
    
    def get_verification_request_info(self, obj):
        """Get latest verification request info"""
        latest_request = obj.verification_requests.order_by('-request_date').first()
        if latest_request:
            return VerificationRequestMinimalSerializer(latest_request).data
        return None


class VolunteerSkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating volunteer skills"""
    
    skill_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = VolunteerSkill
        fields = [
            'skill_id',
            'proficiency_level',
            'last_used_date',
            'supporting_document',
            'supporting_url',
            'is_primary'
        ]
    
    def validate_skill_id(self, value):
        """Validate skill exists and is active"""
        try:
            skill = Skill.objects.get(id=value, is_active=True)
            return value
        except Skill.DoesNotExist:
            raise serializers.ValidationError("Skill not found or inactive.")
    
    def validate_proficiency_level(self, value):
        """Validate proficiency level is valid"""
        valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid proficiency level: {value}")
        return value


class VolunteerSkillUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating volunteer skills"""
    
    class Meta:
        model = VolunteerSkill
        fields = [
            'proficiency_level',
            'last_used_date',
            'supporting_document',
            'supporting_url',
            'is_primary'
        ]
    
    def validate_proficiency_level(self, value):
        """Validate proficiency level is valid"""
        valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid proficiency level: {value}")
        return value


class VolunteerSkillVerifySerializer(serializers.Serializer):
    """Serializer for verifying volunteer skills"""
    
    verification_status = serializers.ChoiceField(
        choices=[
            (SkillVerificationStatus.VERIFIED, 'Verified'),
            (SkillVerificationStatus.REJECTED, 'Rejected')
        ]
    )
    verification_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate_verification_status(self, value):
        """Validate verification status"""
        if value not in [SkillVerificationStatus.VERIFIED, SkillVerificationStatus.REJECTED]:
            raise serializers.ValidationError(
                "Verification status must be VERIFIED or REJECTED."
            )
        return value


class VerificationRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating verification requests"""
    
    documents = serializers.FileField(required=False, allow_null=True)
    links = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=[]
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )


class VerificationRequestReviewSerializer(serializers.Serializer):
    """Serializer for reviewing verification requests"""
    
    verification_request_id = serializers.UUIDField()
    review_status = serializers.ChoiceField(
        choices=[
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('needs_more_info', 'Needs More Information'),
            ('under_review', 'Under Review')
        ]
    )
    review_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )
    admin_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )


class VerificationRequestMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for verification requests"""
    
    volunteer_email = serializers.CharField(source='volunteer_skill.volunteer.user.email', read_only=True)
    skill_name = serializers.CharField(source='volunteer_skill.skill.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = VerificationRequest
        fields = [
            'id',
            'volunteer_skill',
            'volunteer_email',
            'skill_name',
            'request_date',
            'review_status',
            'review_date',
            'reviewed_by',
            'reviewed_by_name',
            'review_notes'
        ]
        read_only_fields = fields


class VerificationRequestSerializer(serializers.ModelSerializer):
    """Detailed serializer for verification requests"""
    
    volunteer_email = serializers.CharField(source='volunteer_skill.volunteer.user.email', read_only=True)
    volunteer_name = serializers.CharField(source='volunteer_skill.volunteer.user.get_full_name', read_only=True)
    skill_name = serializers.CharField(source='volunteer_skill.skill.name', read_only=True)
    skill_category = serializers.CharField(source='volunteer_skill.skill.category.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = VerificationRequest
        fields = [
            'id',
            'volunteer_skill',
            'volunteer_email',
            'volunteer_name',
            'skill_name',
            'skill_category',
            'request_date',
            'request_documents',
            'request_links',
            'request_notes',
            'review_status',
            'review_date',
            'reviewed_by',
            'reviewed_by_name',
            'review_notes',
            'admin_notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class VolunteerSkillStatisticsSerializer(serializers.Serializer):
    """Serializer for volunteer skill statistics"""
    
    volunteer_id = serializers.UUIDField()
    total_skills = serializers.IntegerField()
    verified_skills = serializers.IntegerField()
    pending_verification = serializers.IntegerField()
    pending_verification_requests = serializers.IntegerField()
    proficiency_distribution = serializers.DictField()
    category_distribution = serializers.DictField()
    primary_skill = serializers.CharField(allow_null=True)


class VolunteerSkillBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing volunteer skills"""
    
    skills = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_skills(self, value):
        """Validate skills data"""
        for skill_data in value:
            if 'skill_id' not in skill_data:
                raise serializers.ValidationError(
                    "Each skill must have a skill_id."
                )
            
            # Validate proficiency level if provided
            proficiency = skill_data.get('proficiency_level')
            if proficiency:
                valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
                if proficiency not in valid_levels:
                    raise serializers.ValidationError(
                        f"Invalid proficiency level: {proficiency}"
                    )
        
        return value


class SkillRequirementCheckSerializer(serializers.Serializer):
    """Serializer for skill requirement check"""
    
    has_all_required = serializers.BooleanField()
    missing_skills = serializers.ListField(child=serializers.CharField())
    missing_skill_ids = serializers.ListField(child=serializers.UUIDField())
    verified_skills = serializers.ListField(child=serializers.UUIDField())
    required_skills = serializers.ListField(child=serializers.UUIDField())