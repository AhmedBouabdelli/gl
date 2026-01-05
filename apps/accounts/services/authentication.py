from .base import BaseService
from .user import UserService
from apps.accounts.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings


class AuthenticationService(BaseService):
    """Handle authentication operations"""

    @staticmethod
    def register_user(email, password, first_name='', last_name='', user_type='volunteer'):
        """Register new user"""
        if User.objects.filter(email=email).exists():
            raise ValueError('Email already registered')

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_active=True
        )

        AuthenticationService.log_info(f'New user registered: {email}')
        return user

    @staticmethod
    def generate_jwt_tokens(user):
        """Generate JWT access and refresh tokens"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    @staticmethod
    def send_verification_email(user):
        """Send email verification link"""
        subject = 'Verify Your Email'
        full_name = UserService.get_full_name(user)
        message = f'Hi {full_name}, please verify your email address.'

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            AuthenticationService.log_info(f'Verification email sent to {user.email}')
        except Exception as e:
            AuthenticationService.log_error('Failed to send verification email', e)
            raise

    @staticmethod
    def send_password_reset_email(user):
        """Send password reset email"""
        subject = 'Reset Your Password'
        full_name = UserService.get_full_name(user)
        message = f'Hi {full_name}, click here to reset your password.'

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            AuthenticationService.log_info(f'Password reset email sent to {user.email}')
        except Exception as e:
            AuthenticationService.log_error('Failed to send password reset email', e)
            raise
