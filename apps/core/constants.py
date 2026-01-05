# core/constants.py

class UserType:
    VOLUNTEER = 'volunteer'
    ORGANIZATION = 'organization'
    ADMIN = 'admin'
    CHOICES = [
        (VOLUNTEER, 'Volunteer'),
        (ORGANIZATION, 'Organization'),
        (ADMIN, 'Administrator'),
    ]


class OrganizationType:
    NGO = 'ngo'
    ASSOCIATION = 'association'
    NON_PROFIT = 'non_profit'
    GOVERNMENT = 'government'
    COMMUNITY = 'community'
    OTHER = 'other'
    CHOICES = [
        (NGO, 'NGO'),
        (ASSOCIATION, 'Association'),
        (NON_PROFIT, 'Non-Profit Organization'),
        (GOVERNMENT, 'Government Entity'),
        (COMMUNITY, 'Community Initiative'),
        (OTHER, 'Other'),
    ]


class AvailabilityType:
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    WEEKENDS = 'weekends'
    EVENINGS = 'evenings'
    FLEXIBLE = 'flexible'
    OCCASIONAL = 'occasional'
    CHOICES = [
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time'),
        (WEEKENDS, 'Weekends Only'),
        (EVENINGS, 'Evenings Only'),
        (FLEXIBLE, 'Flexible'),
        (OCCASIONAL, 'Occasional'),
    ]


class MissionStatus:
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'
    CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ONGOING, 'Ongoing'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (ARCHIVED, 'Archived'),
    ]


class MissionType:
    ONE_TIME = 'one_time'
    RECURRING = 'recurring'
    VIRTUAL = 'virtual'
    HYBRID = 'hybrid'
    URGENT = 'urgent'
    CHOICES = [
        (ONE_TIME, 'One-Time Event'),
        (RECURRING, 'Recurring Opportunity'),
        (VIRTUAL, 'Virtual/Remote'),
        (HYBRID, 'Hybrid'),
        (URGENT, 'Urgent Need'),
    ]


class ParticipationStatus:
    PENDING = 'pending'
    PRESELECTED = 'preselected'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'
    CHOICES = [
        (PENDING, 'Pending Review'),
        (PRESELECTED, 'Preselected'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
        (NO_SHOW, 'No Show'),
    ]


class SkillVerificationStatus:
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'
    NOT_REQUIRED = 'not_required'
    CHOICES = [
        (PENDING, 'Pending Verification'),
        (VERIFIED, 'Verified'),
        (REJECTED, 'Verification Rejected'),
        (NOT_REQUIRED, 'Verification Not Required'),
    ]


class ProficiencyLevel:
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
    CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]


class RequirementLevel:
    NICE_TO_HAVE = 'nice_to_have'
    PREFERRED = 'preferred'
    REQUIRED = 'required'
    CRITICAL = 'critical'
    CHOICES = [
        (NICE_TO_HAVE, 'Nice to Have'),
        (PREFERRED, 'Preferred'),
        (REQUIRED, 'Required'),
        (CRITICAL, 'Critical'),
    ]


class NotificationType:
    APPLICATION_RECEIVED = 'application_received'
    APPLICATION_STATUS_CHANGE = 'application_status_change'
    MISSION_APPROACHING = 'mission_approaching'
    HOURS_VALIDATED = 'hours_validated'
    SKILL_VERIFIED = 'skill_verified'
    NEW_MISSION_MATCH = 'new_mission_match'
    SYSTEM_ANNOUNCEMENT = 'system_announcement'
    CHOICES = [
        (APPLICATION_RECEIVED, 'Application Received'),
        (APPLICATION_STATUS_CHANGE, 'Application Status Change'),
        (MISSION_APPROACHING, 'Mission Approaching'),
        (HOURS_VALIDATED, 'Hours Validated'),
        (SKILL_VERIFIED, 'Skill Verified'),
        (NEW_MISSION_MATCH, 'New Mission Match'),
        (SYSTEM_ANNOUNCEMENT, 'System Announcement'),
    ]


class NotificationChannel:
    IN_APP = 'in_app'
    EMAIL = 'email'
    PUSH = 'push'
    SMS = 'sms'
    CHOICES = [
        (IN_APP, 'In-App Notification'),
        (EMAIL, 'Email'),
        (PUSH, 'Push Notification'),
        (SMS, 'SMS'),
    ]


class ChatGroupStatus:
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    CLOSED = 'closed'
    CHOICES = [
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
        (CLOSED, 'Closed'),
    ]


class MemberRole:
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    MEMBER = 'member'
    CHOICES = [
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (MEMBER, 'Member'),
    ]


class MessageType:
    TEXT = 'text'
    SYSTEM = 'system'
    FILE = 'file'
    ANNOUNCEMENT = 'announcement'
    CHOICES = [
        (TEXT, 'Text Message'),
        (SYSTEM, 'System Message'),
        (FILE, 'File Message'),
        (ANNOUNCEMENT, 'Announcement'),
    ]


class ActionType:
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    STATUS_CHANGE = 'status_change'
    VERIFICATION = 'verification'
    VALIDATION = 'validation'
    LOGIN = 'login'
    LOGOUT = 'logout'
    CHOICES = [
        (CREATE, 'Create'),
        (UPDATE, 'Update'),
        (DELETE, 'Delete'),
        (STATUS_CHANGE, 'Status Change'),
        (VERIFICATION, 'Verification'),
        (VALIDATION, 'Validation'),
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
    ]