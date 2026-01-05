from .base import BaseService
from django.contrib.auth.hashers import check_password, make_password


class UserService(BaseService):
    """Handle user-related operations"""

    @staticmethod
    def get_full_name(user, format='first_last'):
        """Get formatted full name"""
        first_name = (user.first_name or '').strip()
        last_name = (user.last_name or '').strip()

        if format == 'last_first':
            return f'{last_name}, {first_name}'.strip().strip(',').strip()
        elif format == 'uppercase':
            return f'{first_name} {last_name}'.upper().strip()
        elif format == 'initials':
            if first_name and last_name:
                return f'{first_name}{last_name}'.upper()
            return first_name.upper() if first_name else ''
        else:
            return f'{first_name} {last_name}'.strip()

    @staticmethod
    def get_user_type_display(user):
        """Get user type in readable format"""
        type_map = {
            'volunteer': 'Volunteer',
            'organization': 'Organization',
            'admin': 'Administrator',
        }
        return type_map.get(user.user_type, 'Unknown')

    @staticmethod
    def get_initials(user):
        """Get user initials"""
        first = user.first_name.upper() if user.first_name else ''
        last = user.last_name.upper() if user.last_name else ''
        return f'{first}{last}'

    @staticmethod
    def mask_email(email):
        """Mask email for privacy"""
        if not email or '@' not in email:
            return email
        local, domain = email.split('@')
        masked_local = local[:2] + '***' if len(local) > 2 else local + '***'
        return f'{masked_local}@{domain}'

    @staticmethod
    def update_user_profile(user, **kwargs):
        """Update user profile fields"""
        allowed_fields = ['first_name', 'last_name', 'phone_number', 'bio']

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        user.save()
        UserService.log_info(f'User {user.email} profile updated')
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        """Change user password safely"""
        if not check_password(old_password, user.password):
            raise ValueError('Old password is incorrect')

        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters')

        user.password = make_password(new_password)
        user.save()
        UserService.log_info(f'Password changed for user {user.email}')
        return user

    @staticmethod
    def add_rating(user, rating):
        """Add rating to user"""
        if not 0 <= rating <= 5:
            raise ValueError('Rating must be between 0 and 5')
        user.rating = rating
        user.save()
        return user

    @staticmethod
    def deactivate_account(user, reason=''):
        """Deactivate user account"""
        user.is_active = False
        if reason:
            user.deactivation_reason = reason
        user.save()
        return user

    @staticmethod
    def reactivate_account(user):
        """Reactivate account"""
        user.is_active = True
        user.deactivation_reason = ''
        user.save()
        return user
