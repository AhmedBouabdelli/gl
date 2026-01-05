"""
Custom permission classes for DZ-Volunteer platform
Updated with Skills Module support
"""
from rest_framework import permissions


# ============ PROFILE OWNERSHIP PERMISSIONS ============

class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission to only allow organization owners to edit their profile.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsVolunteerOwner(permissions.BasePermission):
    """
    Permission to only allow volunteer owners to edit their profile.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsMissionOwner(permissions.BasePermission):
    """
    Permission to only allow mission owners to edit their mission.
    """
    def has_object_permission(self, request, view, obj):
        return obj.organization.user == request.user


# ============ ROLE-BASED PERMISSIONS (PRODUCTION-READY) ============

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin/staff users.
    Admins have full access to all resources.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOrganization(permissions.BasePermission):
    """
    Permission to only allow organization users.
    Organizations can create missions and search volunteers.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'organization_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        # For organization-owned objects, check if user owns it
        if hasattr(obj, 'organization'):
            return obj.organization.user == request.user
        return self.has_permission(request, view)


class IsVolunteer(permissions.BasePermission):
    """
    Permission to only allow volunteer users.
    Volunteers can manage their own skills and apply to missions.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'volunteer_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        # For volunteer-owned objects, check if user owns it
        if hasattr(obj, 'volunteer'):
            return obj.volunteer.user == request.user
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners of an object or admins to access it.
    Used for resources that can be edited by owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user and request.user.is_staff:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For volunteer skills
        if hasattr(obj, 'volunteer'):
            return obj.volunteer.user == request.user
        
        # For mission skills
        if hasattr(obj, 'mission') and hasattr(obj.mission, 'organization'):
            return obj.mission.organization.user == request.user
        
        return False


class IsMissionOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow mission owners or admins to modify mission-related resources.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins can always access
        if request.user.is_staff:
            return True
        
        # Organizations can access (ownership checked at object level)
        return hasattr(request.user, 'organization_profile')
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user and request.user.is_staff:
            return True
        
        # Check if user's organization owns the mission
        if hasattr(obj, 'mission'):
            return obj.mission.organization.user == request.user
        
        # If obj is the mission itself
        if hasattr(obj, 'organization'):
            return obj.organization.user == request.user
        
        return False


# ============ COMBINED PERMISSIONS ============

class IsOrganizationOrAdmin(permissions.BasePermission):
    """
    Permission to allow organization users or admins.
    Used for volunteer search and mission management.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins
        if request.user.is_staff:
            return True
        
        # Allow organizations
        return hasattr(request.user, 'organization_profile')
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsVolunteerOrAdmin(permissions.BasePermission):
    """
    Permission to allow volunteer users or admins.
    Used for volunteer skill management.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins
        if request.user.is_staff:
            return True
        
        # Allow volunteers
        return hasattr(request.user, 'volunteer_profile')
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user and request.user.is_staff:
            return True
        
        # Volunteers can only access their own objects
        if hasattr(obj, 'volunteer'):
            return obj.volunteer.user == request.user
        
        return False


# ============ SKILL-SPECIFIC PERMISSIONS ============

class CanCreateSkillCategory(permissions.BasePermission):
    """
    Permission to allow only admins to create skill categories.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )


class CanCreateSkill(permissions.BasePermission):
    """
    Permission to allow only admins to create skills.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )


class CanVerifySkills(permissions.BasePermission):
    """
    Permission to allow only admins to verify volunteer skills.
    This is a critical action that requires admin privileges.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanReviewVerificationRequests(permissions.BasePermission):
    """
    Permission to allow only admins to review verification requests.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )


class CanManageOwnSkills(permissions.BasePermission):
    """
    Permission for volunteers to manage their own skills.
    Volunteers can add/update/delete only their own skills.
    """
    def has_permission(self, request, view):
        # For list/create, check if user is volunteer
        if request.method in ['GET', 'POST']:
            return (
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'volunteer_profile')
            )
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if the volunteer skill belongs to this user
        if hasattr(obj, 'volunteer'):
            return obj.volunteer.user == request.user
        return False


class CanViewOwnSkills(permissions.BasePermission):
    """
    Permission for volunteers to view only their own skills.
    Admins can view all skills.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins can access all
        if request.user.is_staff:
            return True
        
        # Volunteers can access
        return hasattr(request.user, 'volunteer_profile')
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user and request.user.is_staff:
            return True
        
        # Volunteers can only access their own objects
        if hasattr(obj, 'volunteer'):
            return obj.volunteer.user == request.user
        
        return False


class CanSearchVolunteers(permissions.BasePermission):
    """
    Permission for organizations and admins to search volunteers.
    Regular volunteers cannot search other volunteers (privacy).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins
        if request.user.is_staff:
            return True
        
        # Allow organizations
        if hasattr(request.user, 'organization_profile'):
            return True
        
        # Deny volunteers (privacy protection)
        return False


class CanManageMissionSkills(permissions.BasePermission):
    """
    Permission for organizations to manage their mission skill requirements.
    Admins can manage all mission skills.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins can manage all
        if request.user.is_staff:
            return True
        
        # Organizations can manage their own missions
        return hasattr(request.user, 'organization_profile')
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user and request.user.is_staff:
            return True
        
        # Organizations can only manage their own mission skills
        if hasattr(obj, 'mission'):
            return obj.mission.organization.user == request.user
        
        return False


# ============ PUBLIC ACCESS PERMISSIONS ============

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to unauthenticated users.
    Require authentication for write operations.
    """
    def has_permission(self, request, view):
        # Allow read-only methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class ReadOnly(permissions.BasePermission):
    """
    Allow only read-only access (GET, HEAD, OPTIONS).
    Deny all write operations.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


# ============ TEST PERMISSIONS (REMOVE BEFORE PRODUCTION!) ============

class AllowAnyForTesting(permissions.BasePermission):
    """
    ⚠️ TESTING ONLY - REMOVE BEFORE PRODUCTION! ⚠️
    
    Allows any request for testing purposes without authentication.
    This bypasses ALL security checks and should NEVER be used in production.
    """
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        return True


# ============ PERMISSION COMBINATIONS (HELPERS) ============

def get_skill_category_permissions(action):
    """
    Helper to get appropriate permissions for skill category actions.
    
    Rules:
    - list/retrieve/tree: Public read access
    - create/update/delete: Admin only
    """
    if action in ['list', 'retrieve', 'tree', 'roots', 'path', 'search']:
        # Public read access
        return [IsAuthenticatedOrReadOnly()]
    elif action in ['create', 'update', 'partial_update', 'destroy']:
        # Only admins can modify categories
        return [CanCreateSkillCategory()]
    return [permissions.IsAuthenticated()]


def get_skill_permissions(action):
    """
    Helper to get appropriate permissions for skill actions.
    
    Rules:
    - list/retrieve/by_category/search/popular: Public read access
    - create/update/delete: Admin only
    """
    if action in ['list', 'retrieve', 'by_category', 'search', 'popular', 'statistics']:
        # Public read access
        return [IsAuthenticatedOrReadOnly()]
    elif action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
        # Only admins can modify skills
        return [CanCreateSkill()]
    return [permissions.IsAuthenticated()]


def get_volunteer_skill_permissions(action):
    """
    Helper to get appropriate permissions for volunteer skill actions.
    
    Rules:
    - verify/review_verification: Admin only
    - pending_verification_requests: Admin only
    - request_verification: Volunteer can request for own skills
    - verification_requests: Volunteer can view own verification requests
    - create/update/delete/bulk_import: Volunteer can manage own skills
    - list/retrieve: Volunteer sees own, admin sees all
    - statistics/suggestions: Volunteer sees own, admin sees all
    - check_requirements/verified: Volunteer sees own, admin sees all
    """
    if action in ['verify', 'review_verification', 'pending_verification_requests']:
        # Only admins can verify skills and review requests
        return [CanVerifySkills() | CanReviewVerificationRequests()]
    elif action in ['request_verification']:
        # Volunteers can request verification for their own skills
        return [CanManageOwnSkills()]
    elif action in ['verification_requests']:
        # Volunteers can view verification requests for their own skills
        return [CanViewOwnSkills()]
    elif action in ['create', 'update', 'partial_update', 'destroy', 'bulk_import']:
        # Volunteers can manage their own skills
        return [CanManageOwnSkills()]
    elif action in ['list', 'retrieve', 'statistics', 'suggestions', 'check_requirements', 'verified']:
        # Volunteers see own, admins see all
        return [CanViewOwnSkills()]
    return [permissions.IsAuthenticated()]


def get_mission_skill_permissions(action):
    """
    Helper to get appropriate permissions for mission skill actions.
    
    Rules:
    - list/retrieve/required: Public read access
    - create/update/delete/bulk_add: Mission owners and admins can modify
    - suggestions/validate_volunteer: Mission owners and admins
    - statistics: Mission owners and admins
    """
    if action in ['list', 'retrieve', 'required']:
        # Public read access
        return [IsAuthenticatedOrReadOnly()]
    elif action in ['create', 'update', 'partial_update', 'destroy', 'bulk_add']:
        # Mission owners and admins can modify
        return [CanManageMissionSkills()]
    elif action in ['suggestions', 'validate_volunteer', 'statistics']:
        # Mission owners and admins
        return [CanManageMissionSkills()]
    return [permissions.IsAuthenticated()]


def get_volunteer_search_permissions(action):
    """
    Helper to get appropriate permissions for volunteer search actions.
    
    Rules:
    - Only organizations and admins can search volunteers
    """
    return [CanSearchVolunteers()]