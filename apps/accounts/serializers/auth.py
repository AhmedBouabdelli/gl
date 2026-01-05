from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import re
import os
from django.conf import settings

from apps.accounts.models import User
from apps.core.constants import UserType


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    user_type = serializers.ChoiceField(
        choices=UserType.CHOICES,  # CHANGED: Use all choices including admin
        required=True
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    
    # NEW: Optional invitation code for admin registration
    invitation_code = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True
    )
    
    def validate_email(self, value):
        email = value.lower().strip()
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _('A user with this email already exists.')
            )
        
        return email
    
    def validate_phone_number(self, value):
        if not value:
            return value
        
        cleaned = value.replace(' ', '').replace('-', '')
        
        pattern = r'^(\+213|0)[5-7][0-9]{8}$'
        
        if not re.match(pattern, cleaned):
            raise serializers.ValidationError(
                _('Enter a valid Algerian phone number. Format: +213XXXXXXXXX or 0XXXXXXXXX')
            )
        
        return value
    
    def validate_user_type(self, value):
        """NEW: Security check for admin registration"""
        # If trying to register as admin
        if value == UserType.ADMIN:
            invitation_code = self.initial_data.get('invitation_code', '')
            expected_code = getattr(settings, 'ADMIN_REGISTRATION_CODE', 'DEFAULT_SECURE_CODE')
            
            if invitation_code != expected_code:
                raise serializers.ValidationError(
                    _('Valid invitation code required for admin registration.')
                )
        
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': _('Passwords do not match.')
            })
        
        # NEW: Remove invitation code from attrs (not needed in user creation)
        attrs.pop('invitation_code', None)
        
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user_type = validated_data.pop('user_type')
        phone_number = validated_data.pop('phone_number', None)
        
        user = User.objects.create(
            email=email,
            username=email.split('@')[0],
            user_type=user_type,
            phone_number=phone_number,
            **validated_data
        )
        
        # NEW: Auto-set Django admin flags for admin users
        if user_type == UserType.ADMIN:
            user.is_staff = True
            user.is_superuser = True
            user.is_verified = True  # Auto-verify admins
        
        user.set_password(password)
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,  
            password=password
        )
        
        if not user:
            raise serializers.ValidationError(
                _('Invalid email or password.'),
                code='authentication_failed'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                _('This account has been deactivated.'),
                code='account_inactive'
            )
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Old password is incorrect.')
            )
        
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('New passwords do not match.')
            })
        
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if email exists."""
        email = value.lower().strip()
        
        try:
            user = User.objects.get(email=email, is_active=True)
            self.context['user'] = user
        except User.DoesNotExist:
            pass
        
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):    
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': _('Invalid reset link.')})
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': _('Invalid or expired token.')})
        
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Passwords do not match.')
            })
        
        attrs['user'] = user
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user