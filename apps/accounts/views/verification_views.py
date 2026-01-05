from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from apps.accounts.models import User
from apps.accounts.services import AuthenticationService


class SendVerificationEmailView(APIView):
    """Send email verification link"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_active=True)

            if user.is_verified:
                return Response(
                    {'message': 'Email already verified.'},
                    status=status.HTTP_200_OK
                )

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

            send_mail(
                subject='Verify Your Email - DZ-Volunteer',
                message=f'Click the link to verify your email: {verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {'message': 'Verification email sent.'},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response(
                {'message': 'If the email exists, a verification link has been sent.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to send verification email.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailView(APIView):
    """Verify user email with token"""
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')

        if not uid or not token:
            return Response(
                {'error': 'UID and token are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid verification link.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save(update_fields=['is_verified'])

            return Response(
                {'message': 'Email verified successfully.'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Invalid or expired verification link.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResendVerificationEmailView(APIView):
    """Resend verification email for authenticated user"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_verified:
            return Response(
                {'message': 'Email already verified.'},
                status=status.HTTP_200_OK
            )

        try:
            AuthenticationService.send_verification_email(user)

            return Response(
                {
                    'message': 'Verification email sent successfully.',
                    'email': user.email
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': 'Failed to send verification email.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckEmailVerificationView(APIView):
    """Check email verification status"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(
            {
                'email': user.email,
                'is_verified': user.is_verified,
                'message': 'Email verified' if user.is_verified else 'Email not verified'
            },
            status=status.HTTP_200_OK
        )