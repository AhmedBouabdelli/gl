from django.db import transaction, models
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from typing import List, Optional, Dict, Any
from ..models import VolunteerSkill, VerificationRequest
from apps.core.constants import SkillVerificationStatus


class VerificationService:
    """Service for managing verification requests"""
    
    @staticmethod
    @transaction.atomic
    def request_verification(
        volunteer_skill_id: str,
        documents: Optional[Any] = None,
        links: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> VerificationRequest:
        """Request verification for a volunteer skill"""
        try:
            volunteer_skill = VolunteerSkill.objects.select_related(
                'skill'
            ).get(id=volunteer_skill_id)
        except VolunteerSkill.DoesNotExist:
            raise ValidationError("Volunteer skill not found.")
        
        # Check if verification can be requested
        if not volunteer_skill.can_request_verification():
            raise ValidationError(
                "Verification cannot be requested for this skill. "
                "It may already be verified, not require verification, "
                "or already have a pending verification request."
            )
        
        # Create verification request
        verification_request = VerificationRequest.objects.create(
            volunteer_skill=volunteer_skill,
            request_documents=documents,
            request_links=links or [],
            request_notes=notes or ''
        )
        
        # Update volunteer skill to mark verification requested
        volunteer_skill.verification_requested = True
        volunteer_skill.verification_request_date = timezone.now()
        if documents:
            volunteer_skill.verification_documents = documents
        if links:
            volunteer_skill.verification_links = links
        volunteer_skill.save()
        
        return verification_request
    
    @staticmethod
    def get_verification_requests_for_skill(
        volunteer_skill_id: str
    ) -> List[VerificationRequest]:
        """Get all verification requests for a volunteer skill"""
        return VerificationRequest.objects.filter(
            volunteer_skill_id=volunteer_skill_id
        ).select_related(
            'volunteer_skill',
            'volunteer_skill__volunteer__user',
            'volunteer_skill__skill',
            'volunteer_skill__skill__category',
            'reviewed_by'
        ).order_by('-request_date')
    
    @staticmethod
    def get_pending_verification_requests() -> List[VerificationRequest]:
        """Get all pending verification requests"""
        return VerificationRequest.objects.filter(
            review_status__in=['pending', 'under_review', 'needs_more_info']
        ).select_related(
            'volunteer_skill',
            'volunteer_skill__volunteer__user',
            'volunteer_skill__skill',
            'volunteer_skill__skill__category',
            'reviewed_by'
        ).order_by('-request_date')
    
    @staticmethod
    @transaction.atomic
    def review_verification_request(
        verification_request_id: str,
        reviewer_id: str,
        review_status: str,
        review_notes: Optional[str] = None,
        admin_notes: Optional[str] = None
    ) -> VerificationRequest:
        """Review a verification request (admin action)"""
        try:
            verification_request = VerificationRequest.objects.select_related(
                'volunteer_skill',
                'volunteer_skill__skill'
            ).get(id=verification_request_id)
        except VerificationRequest.DoesNotExist:
            raise ValidationError("Verification request not found.")
        
        # Update verification request
        verification_request.reviewed_by_id = reviewer_id
        verification_request.review_date = timezone.now()
        verification_request.review_status = review_status
        verification_request.review_notes = review_notes or ''
        verification_request.admin_notes = admin_notes or ''
        verification_request.save()
        
        # Update volunteer skill based on review status
        volunteer_skill = verification_request.volunteer_skill
        
        if review_status == 'approved':
            # Mark skill as verified
            volunteer_skill.verification_status = SkillVerificationStatus.VERIFIED
            volunteer_skill.verified_by_id = reviewer_id
            volunteer_skill.verification_date = timezone.now()
            volunteer_skill.verification_notes = f"Approved via verification request: {review_notes}"
            volunteer_skill.verification_requested = False
        elif review_status == 'rejected':
            # Keep as pending but note the rejection
            volunteer_skill.verification_notes = f"Verification request rejected: {review_notes}"
            volunteer_skill.verification_requested = False
        elif review_status == 'needs_more_info':
            # Keep verification requested but update notes
            volunteer_skill.verification_notes = f"Needs more information: {review_notes}"
        
        volunteer_skill.save()
        
        return verification_request
    
    @staticmethod
    def get_verification_request_stats() -> Dict[str, Any]:
        """Get statistics about verification requests"""
        total = VerificationRequest.objects.count()
        pending = VerificationRequest.objects.filter(
            review_status='pending'
        ).count()
        under_review = VerificationRequest.objects.filter(
            review_status='under_review'
        ).count()
        approved = VerificationRequest.objects.filter(
            review_status='approved'
        ).count()
        rejected = VerificationRequest.objects.filter(
            review_status='rejected'
        ).count()
        needs_more_info = VerificationRequest.objects.filter(
            review_status='needs_more_info'
        ).count()
        
        return {
            'total_requests': total,
            'pending_review': pending,
            'under_review': under_review,
            'approved': approved,
            'rejected': rejected,
            'needs_more_info': needs_more_info,
        }
    
    @staticmethod
    def get_verification_requests_by_volunteer(
        volunteer_id: str
    ) -> List[VerificationRequest]:
        """Get all verification requests for a volunteer"""
        return VerificationRequest.objects.filter(
            volunteer_skill__volunteer_id=volunteer_id
        ).select_related(
            'volunteer_skill',
            'volunteer_skill__skill',
            'volunteer_skill__skill__category',
            'reviewed_by'
        ).order_by('-request_date')