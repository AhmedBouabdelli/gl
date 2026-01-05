
from rest_framework import serializers
from ..models import Skill, SkillCategory


class SkillCategoryMinimalSerializer(serializers.ModelSerializer):
  
    
    class Meta:
        model = SkillCategory
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class SkillListSerializer(serializers.ModelSerializer):
   
    
    category = SkillCategoryMinimalSerializer(read_only=True)
    verification_requirement_display = serializers.CharField(
        source='get_verification_requirement_display',
        read_only=True
    )
    
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'description',
            'category',
            'verification_requirement',
            'verification_requirement_display',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SkillDetailSerializer(serializers.ModelSerializer):
    
    
    category = SkillCategoryMinimalSerializer(read_only=True)
    verification_requirement_display = serializers.CharField(
        source='get_verification_requirement_display',
        read_only=True
    )
    volunteer_count = serializers.IntegerField(read_only=True)
    mission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'description',
            'category',
            'verification_requirement',
            'verification_requirement_display',
            'is_active',
            'volunteer_count',
            'mission_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'volunteer_count', 'mission_count']


class SkillCreateSerializer(serializers.ModelSerializer):
   
    
    class Meta:
        model = Skill
        fields = [
            'name',
            'description',
            'category',
            'verification_requirement',
            'is_active'
        ]
    
    def validate_name(self, value):
        
        name = value.strip().title()
        if Skill.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError(
                f"Skill with name '{name}' already exists."
            )
        return name
    
    def validate_category(self, value):
       
        if not SkillCategory.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Category not found.")
        return value


class SkillUpdateSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Skill
        fields = [
            'name',
            'description',
            'category',
            'verification_requirement',
            'is_active'
        ]
    
    def validate_name(self, value):
        """Validate skill name is unique (excluding current skill)"""
        name = value.strip().title()
        skill_id = self.instance.id if self.instance else None
        
        if Skill.objects.filter(name__iexact=name).exclude(id=skill_id).exists():
            raise serializers.ValidationError(
                f"Skill with name '{name}' already exists."
            )
        return name


class SkillMinimalSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Skill
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class SkillStatisticsSerializer(serializers.Serializer):
    
    
    skill_id = serializers.UUIDField()
    skill_name = serializers.CharField()
    category = serializers.CharField()
    is_active = serializers.BooleanField()
    verification_requirement = serializers.CharField()
    total_volunteers = serializers.IntegerField()
    verification_breakdown = serializers.DictField()
    total_missions = serializers.IntegerField()
    requirement_breakdown = serializers.DictField()