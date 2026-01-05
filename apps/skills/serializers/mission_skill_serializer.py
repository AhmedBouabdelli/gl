
from rest_framework import serializers
from ..models import MissionSkill, Skill
from apps.core.constants import RequirementLevel, ProficiencyLevel


class SkillInfoSerializer(serializers.ModelSerializer):
    
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'category_name',
            'verification_requirement'
        ]
        read_only_fields = fields


class MissionSkillListSerializer(serializers.ModelSerializer):
 
    
    skill = SkillInfoSerializer(read_only=True)
    requirement_level_display = serializers.CharField(
        source='get_requirement_level_display',
        read_only=True
    )
    min_proficiency_level_display = serializers.CharField(
        source='get_min_proficiency_level_display',
        read_only=True
    )
    
    class Meta:
        model = MissionSkill
        fields = [
            'id',
            'skill',
            'requirement_level',
            'requirement_level_display',
            'is_verification_required',
            'min_proficiency_level',
            'min_proficiency_level_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MissionSkillDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for mission skill requirement"""
    
    skill = SkillInfoSerializer(read_only=True)
    requirement_level_display = serializers.CharField(
        source='get_requirement_level_display',
        read_only=True
    )
    min_proficiency_level_display = serializers.CharField(
        source='get_min_proficiency_level_display',
        read_only=True
    )
    is_required_skill = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MissionSkill
        fields = [
            'id',
            'skill',
            'requirement_level',
            'requirement_level_display',
            'is_verification_required',
            'is_required_skill',
            'min_proficiency_level',
            'min_proficiency_level_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'is_required_skill', 'created_at', 'updated_at']


class MissionSkillCreateSerializer(serializers.ModelSerializer):
   
    
    skill_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MissionSkill
        fields = [
            'skill_id',
            'requirement_level',
            'is_verification_required',
            'min_proficiency_level'
        ]
    
    def validate_skill_id(self, value):
        """Validate skill exists and is active"""
        try:
            Skill.objects.get(id=value, is_active=True)
            return value
        except Skill.DoesNotExist:
            raise serializers.ValidationError("Skill not found or inactive.")
    
    def validate_requirement_level(self, value):
        """Validate requirement level"""
        valid_levels = [choice[0] for choice in RequirementLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid requirement level: {value}")
        return value
    
    def validate_min_proficiency_level(self, value):
        """Validate proficiency level"""
        valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid proficiency level: {value}")
        return value


class MissionSkillUpdateSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = MissionSkill
        fields = [
            'requirement_level',
            'is_verification_required',
            'min_proficiency_level'
        ]
    
    def validate_requirement_level(self, value):
        """Validate requirement level"""
        valid_levels = [choice[0] for choice in RequirementLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid requirement level: {value}")
        return value
    
    def validate_min_proficiency_level(self, value):
        """Validate proficiency level"""
        valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid proficiency level: {value}")
        return value


class MissionSkillStatisticsSerializer(serializers.Serializer):
   
    
    mission_id = serializers.UUIDField()
    total_skills = serializers.IntegerField()
    requirement_breakdown = serializers.DictField()
    verification_required_count = serializers.IntegerField()
    category_breakdown = serializers.DictField()
    critical_skills = serializers.ListField(child=serializers.CharField())
    critical_skills_count = serializers.IntegerField()


class MissionSkillBulkCreateSerializer(serializers.Serializer):
   
    
    skills = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_skills(self, value):
       
        for skill_data in value:
            if 'skill_id' not in skill_data:
                raise serializers.ValidationError(
                    "Each skill must have a skill_id."
                )
            
            
            req_level = skill_data.get('requirement_level')
            if req_level:
                valid_levels = [choice[0] for choice in RequirementLevel.CHOICES]
                if req_level not in valid_levels:
                    raise serializers.ValidationError(
                        f"Invalid requirement level: {req_level}"
                    )
            
           
            prof_level = skill_data.get('min_proficiency_level')
            if prof_level:
                valid_levels = [choice[0] for choice in ProficiencyLevel.CHOICES]
                if prof_level not in valid_levels:
                    raise serializers.ValidationError(
                        f"Invalid proficiency level: {prof_level}"
                    )
        
        return value


class MissionSkillValidationSerializer(serializers.Serializer):
   
    
    can_apply = serializers.BooleanField()
    has_all_required = serializers.BooleanField()
    missing_skills = serializers.ListField(child=serializers.DictField())
    total_required_skills = serializers.IntegerField()
    missing_count = serializers.IntegerField()


class MissionSkillMinimalSerializer(serializers.ModelSerializer):
    
    
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    requirement_level_display = serializers.CharField(
        source='get_requirement_level_display',
        read_only=True
    )
    
    class Meta:
        model = MissionSkill
        fields = [
            'id',
            'skill_name',
            'requirement_level',
            'requirement_level_display',
            'is_verification_required'
        ]
        read_only_fields = fields