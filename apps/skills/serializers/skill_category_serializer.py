
from rest_framework import serializers
from ..models import SkillCategory


class SkillCategoryListSerializer(serializers.ModelSerializer):
    
    
    parent_category_name = serializers.CharField(
        source='parent_category.name',
        read_only=True,
        allow_null=True
    )
    subcategories_count = serializers.IntegerField(read_only=True)
    skills_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SkillCategory
        fields = [
            'id',
            'name',
            'description',
            'parent_category',
            'parent_category_name',
            'subcategories_count',
            'skills_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SkillCategoryDetailSerializer(serializers.ModelSerializer):
    
    
    parent_category_name = serializers.CharField(
        source='parent_category.name',
        read_only=True,
        allow_null=True
    )
    subcategories = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillCategory
        fields = [
            'id',
            'name',
            'description',
            'parent_category',
            'parent_category_name',
            'subcategories',
            'skills',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subcategories(self, obj):
        """Get list of subcategories"""
        subcategories = obj.subcategories.all()
        return [
            {
                'id': str(sub.id),
                'name': sub.name,
                'description': sub.description
            }
            for sub in subcategories
        ]
    
    def get_skills(self, obj):
        """Get list of skills in this category"""
        skills = obj.skills.filter(is_active=True)
        return [
            {
                'id': str(skill.id),
                'name': skill.name,
                'verification_requirement': skill.get_verification_requirement_display()
            }
            for skill in skills
        ]


class SkillCategoryCreateSerializer(serializers.ModelSerializer):
   
    
    class Meta:
        model = SkillCategory
        fields = [
            'name',
            'description',
            'parent_category'
        ]
    
    def validate_name(self, value):
        
        name = value.strip().title()
        if SkillCategory.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError(
                f"Category with name '{name}' already exists."
            )
        return name
    
    def validate_parent_category(self, value):
        
        if value and not SkillCategory.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Parent category not found.")
        return value


class SkillCategoryUpdateSerializer(serializers.ModelSerializer):
   
    
    class Meta:
        model = SkillCategory
        fields = [
            'name',
            'description',
            'parent_category'
        ]
    
    def validate_name(self, value):
       
        name = value.strip().title()
        category_id = self.instance.id if self.instance else None
        
        if SkillCategory.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            raise serializers.ValidationError(
                f"Category with name '{name}' already exists."
            )
        return name
    
    def validate_parent_category(self, value):
        
        if not value:
            return value
        
        # Check if parent exists
        if not SkillCategory.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Parent category not found.")
        
        # Prevent setting self as parent
        if self.instance and value.id == self.instance.id:
            raise serializers.ValidationError(
                "Category cannot be its own parent."
            )
        
        # Check for circular reference
        current = value
        while current:
            if self.instance and current.id == self.instance.id:
                raise serializers.ValidationError(
                    "Cannot set parent: would create circular reference."
                )
            current = current.parent_category
        
        return value


class SkillCategoryTreeSerializer(serializers.Serializer):
    
    
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    skills_count = serializers.IntegerField()
    subcategories = serializers.ListField(child=serializers.DictField())


class SkillCategoryPathSerializer(serializers.Serializer):
   
    
    id = serializers.UUIDField()
    name = serializers.CharField()
    level = serializers.IntegerField()


class SkillCategoryStatisticsSerializer(serializers.Serializer):
    
    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    total_skills = serializers.IntegerField()
    total_subcategories = serializers.IntegerField()
    total_volunteers = serializers.IntegerField()
    depth_level = serializers.IntegerField()


class SkillCategoryMinimalSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = SkillCategory
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']