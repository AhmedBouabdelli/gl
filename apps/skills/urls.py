"""
Skills URL Configuration
Explicit URL patterns for all ViewSets
"""
from django.urls import path
from .views import (
    SkillCategoryViewSet,
    SkillViewSet,
    VolunteerSkillViewSet,
    MissionSkillViewSet,
    VolunteerSearchViewSet,
)

app_name = 'skills'

# ============ Skill Category URLs ============
urlpatterns = [
    # Skill Category List/Create
    path('skill-categories/', 
         SkillCategoryViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='skill-category-list-create'),
    
    # Skill Category Detail/Update/Delete
    path('skill-categories/<uuid:id>/', 
         SkillCategoryViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='skill-category-detail'),
    
    # Skill Category Actions
    path('skill-categories/tree/', 
         SkillCategoryViewSet.as_view({'get': 'tree'}), 
         name='skill-category-tree'),
    
    path('skill-categories/<uuid:id>/statistics/', 
         SkillCategoryViewSet.as_view({'get': 'statistics'}), 
         name='skill-category-statistics'),
    
    path('skill-categories/<uuid:id>/path/', 
         SkillCategoryViewSet.as_view({'get': 'path'}), 
         name='skill-category-path'),
    
    path('skill-categories/roots/', 
         SkillCategoryViewSet.as_view({'get': 'roots'}), 
         name='skill-category-roots'),
    
    path('skill-categories/search/', 
         SkillCategoryViewSet.as_view({'get': 'search'}), 
         name='skill-category-search'),
]

# ============ Skill URLs ============
urlpatterns += [
    # Skill List/Create
    path('skills/', 
         SkillViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='skill-list-create'),
    
    # Skill Detail/Update/Delete
    path('skills/<uuid:id>/', 
         SkillViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='skill-detail'),
    
    # Skill Actions
    path('skills/popular/', 
         SkillViewSet.as_view({'get': 'popular'}), 
         name='skill-popular'),
    
    path('skills/<uuid:id>/statistics/', 
         SkillViewSet.as_view({'get': 'statistics'}), 
         name='skill-statistics'),
    
    path('skills/<uuid:id>/activate/', 
         SkillViewSet.as_view({'post': 'activate'}), 
         name='skill-activate'),
    
    path('skills/<uuid:id>/deactivate/', 
         SkillViewSet.as_view({'post': 'deactivate'}), 
         name='skill-deactivate'),
    
    path('skills/search/', 
         SkillViewSet.as_view({'get': 'search'}), 
         name='skill-search'),
    
    path('skills/by_category/', 
         SkillViewSet.as_view({'get': 'by_category'}), 
         name='skill-by-category'),
]

# ============ Volunteer Skill URLs ============
urlpatterns += [
    # Volunteer Skill List/Create
    path('volunteer-skills/', 
         VolunteerSkillViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='volunteer-skill-list-create'),
    
    # Volunteer Skill Detail/Update/Delete
    path('volunteer-skills/<uuid:id>/', 
         VolunteerSkillViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='volunteer-skill-detail'),
    
    # Verification Requests
    path('volunteer-skills/<uuid:id>/request-verification/', 
         VolunteerSkillViewSet.as_view({'post': 'request_verification'}), 
         name='request-verification'),
    
    path('volunteer-skills/<uuid:id>/verification-requests/', 
         VolunteerSkillViewSet.as_view({'get': 'verification_requests'}), 
         name='verification-requests'),
    
    path('volunteer-skills/pending-verification-requests/', 
         VolunteerSkillViewSet.as_view({'get': 'pending_verification_requests'}), 
         name='pending-verification-requests'),
    
    path('volunteer-skills/review-verification/', 
         VolunteerSkillViewSet.as_view({'post': 'review_verification'}), 
         name='review-verification-general'),
    
    path('volunteer-skills/<uuid:id>/review-verification/', 
         VolunteerSkillViewSet.as_view({'post': 'review_verification'}), 
         name='review-verification-specific'),
    
    # Statistics and Suggestions
    path('volunteer-skills/statistics/', 
         VolunteerSkillViewSet.as_view({'get': 'statistics'}), 
         name='statistics'),
    
    path('volunteer-skills/suggestions/', 
         VolunteerSkillViewSet.as_view({'get': 'suggestions'}), 
         name='suggestions'),
    
    # Bulk Operations
    path('volunteer-skills/bulk-import/', 
         VolunteerSkillViewSet.as_view({'post': 'bulk_import'}), 
         name='bulk-import'),
    
    # Verification Actions
    path('volunteer-skills/<uuid:id>/verify/', 
         VolunteerSkillViewSet.as_view({'post': 'verify'}), 
         name='verify'),
    
    # Requirement Check
    path('volunteer-skills/check-requirements/', 
         VolunteerSkillViewSet.as_view({'post': 'check_requirements'}), 
         name='check-requirements'),
    
    # Verified Skills
    path('volunteer-skills/verified/', 
         VolunteerSkillViewSet.as_view({'get': 'verified'}), 
         name='verified'),
]

# ============ Mission Skill URLs ============
urlpatterns += [
    # Mission Skill List/Create
    path('mission-skills/', 
         MissionSkillViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='mission-skill-list-create'),
    
    # Mission Skill Detail/Update/Delete
    path('mission-skills/<uuid:id>/', 
         MissionSkillViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='mission-skill-detail'),
    
    # Mission Skill Actions
    path('mission-skills/statistics/', 
         MissionSkillViewSet.as_view({'get': 'statistics'}), 
         name='mission-skill-statistics'),
    
    path('mission-skills/bulk_add/', 
         MissionSkillViewSet.as_view({'post': 'bulk_add'}), 
         name='mission-skill-bulk-add'),
    
    path('mission-skills/suggestions/', 
         MissionSkillViewSet.as_view({'get': 'suggestions'}), 
         name='mission-skill-suggestions'),
    
    path('mission-skills/validate_volunteer/', 
         MissionSkillViewSet.as_view({'post': 'validate_volunteer'}), 
         name='mission-skill-validate-volunteer'),
    
    path('mission-skills/required/', 
         MissionSkillViewSet.as_view({'get': 'required'}), 
         name='mission-skill-required'),
]

# ============ Volunteer Search URLs ============
urlpatterns += [
    # Volunteer Search Actions
    path('volunteer-search/by_skills/', 
         VolunteerSearchViewSet.as_view({'get': 'by_skills'}), 
         name='volunteer-search-by-skills'),
    
    path('volunteer-search/by_mission/', 
         VolunteerSearchViewSet.as_view({'get': 'by_mission'}), 
         name='volunteer-search-by-mission'),
    
    path('volunteer-search/by_skill_category/', 
         VolunteerSearchViewSet.as_view({'get': 'by_skill_category'}), 
         name='volunteer-search-by-category'),
]

