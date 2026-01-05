from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    
    CurrentUserView,
    UserDetailView,
    UserUpdateView,
    
    VolunteerProfileView,
    OrganizationProfileView,
    
    SendVerificationEmailView,
    VerifyEmailView,
)


app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('me/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user_detail'),
    
    path('volunteer-profile/', VolunteerProfileView.as_view(), name='volunteer_profile'),
    path('organization-profile/', OrganizationProfileView.as_view(), name='organization_profile'),
    
     path('send-verification-email/', SendVerificationEmailView.as_view(), name='send_verification_email'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
]

