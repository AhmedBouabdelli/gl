"""
Serializers for Volunteer Search Results
Add these to your existing serializers.py file
"""
from rest_framework import serializers


class MatchedSkillSerializer(serializers.Serializer):
    """Serializer for matched skill information"""
    skill_id = serializers.UUIDField()
    skill_name = serializers.CharField()
    category = serializers.CharField()
    proficiency_level = serializers.CharField()
    proficiency_display = serializers.CharField()
    verification_status = serializers.CharField()
    verification_display = serializers.CharField()
    years_of_experience = serializers.FloatField()
    is_primary = serializers.BooleanField()


class VolunteerSearchResultSerializer(serializers.Serializer):
    """Serializer for volunteer search results"""
    volunteer_id = serializers.UUIDField()
    volunteer_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_null=True, allow_blank=True)
    wilaya = serializers.CharField(allow_null=True, allow_blank=True)
    availability = serializers.CharField(allow_null=True, allow_blank=True)
    matched_skills_count = serializers.IntegerField()
    total_required_skills = serializers.IntegerField()
    match_percentage = serializers.FloatField()
    matched_skills = MatchedSkillSerializer(many=True)


class MissionMatchSerializer(serializers.Serializer):
    """Serializer for mission-specific match information"""
    overall_score = serializers.FloatField()
    required_skills_matched = serializers.IntegerField()
    required_skills_total = serializers.IntegerField()
    required_skills_missing = serializers.IntegerField()
    preferred_skills_matched = serializers.IntegerField()
    preferred_skills_total = serializers.IntegerField()
    is_fully_qualified = serializers.BooleanField()


class VolunteerSkillMatchSerializer(serializers.Serializer):
    """Serializer for volunteer with mission match score"""
    volunteer_id = serializers.UUIDField()
    volunteer_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_null=True, allow_blank=True)
    wilaya = serializers.CharField(allow_null=True, allow_blank=True)
    availability = serializers.CharField(allow_null=True, allow_blank=True)
    matched_skills_count = serializers.IntegerField()
    total_required_skills = serializers.IntegerField()
    match_percentage = serializers.FloatField()
    matched_skills = MatchedSkillSerializer(many=True)
    mission_match = MissionMatchSerializer()