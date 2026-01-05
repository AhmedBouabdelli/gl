from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.accounts.models import (
    VolunteerProfile,
    OrganizationProfile,
    User
)
from apps.accounts.serializers import (
    VolunteerProfileSerializer,
    VolunteerProfileUpdateSerializer,
    OrganizationProfileSerializer,
    OrganizationProfileUpdateSerializer,
)
from apps.accounts.permissions import (
    IsOwnerOrAdmin,
    IsVolunteer,
    IsOrganization,
)
from apps.accounts.services import (
    VolunteerProfileService,
    OrganizationProfileService,
)
from apps.core.constants import UserType


class VolunteerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update volunteer profile"""
    permission_classes = [IsAuthenticated, IsVolunteer]
    serializer_class = VolunteerProfileSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VolunteerProfileUpdateSerializer
        return VolunteerProfileSerializer

    def get_object(self):
        user = self.request.user

        # Fixed: Changed User.user_type to user.user_type
        if user.user_type != UserType.VOLUNTEER:
            self.permission_denied(
                self.request,
                message='Only volunteers can access this endpoint.'
            )
        
        profile, created = VolunteerProfile.objects.get_or_create(
            user=user
        )

        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        badge = VolunteerProfileService.get_volunteer_badge(instance)
        stats = VolunteerProfileService.get_volunteer_statistics(instance)

        return Response(
            {
                'profile': serializer.data,
                'badge': badge,
                'stats': stats,
            },
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        profile_serializer = VolunteerProfileSerializer(
            instance,
            context={'request': request}
        )

        badge = VolunteerProfileService.get_volunteer_badge(instance)
        stats = VolunteerProfileService.get_volunteer_statistics(instance)

        return Response(
            {
                'profile': profile_serializer.data,
                'badge': badge,
                'stats': stats,
                'message': 'Volunteer profile updated successfully.'
            },
            status=status.HTTP_200_OK
        )


class OrganizationProfileView(generics.RetrieveUpdateAPIView):
    """Get and update organization profile"""
    permission_classes = [IsAuthenticated, IsOrganization]
    serializer_class = OrganizationProfileSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrganizationProfileUpdateSerializer
        return OrganizationProfileSerializer

    def get_object(self):
        user = self.request.user

        # Fixed: Changed User.user_type to user.user_type
        if user.user_type != UserType.ORGANIZATION:
            self.permission_denied(
                self.request,
                message='Only organizations can access this endpoint.'
            )

        profile, created = OrganizationProfile.objects.get_or_create(
            user=user,
            defaults={
                'name': user.email,  # Fixed: Changed User.email to user.email
                'description': '',
                'organization_type': 'other',
            }
        )

        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        stats = OrganizationProfileService.get_organization_statistics(instance)

        return Response(
            {
                'profile': serializer.data,
                'stats': stats,
            },
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        profile_serializer = OrganizationProfileSerializer(
            instance,
            context={'request': request}
        )

        stats = OrganizationProfileService.get_organization_statistics(instance)

        return Response(
            {
                'profile': profile_serializer.data,
                'stats': stats,
                'message': 'Organization profile updated successfully.'
            },
            status=status.HTTP_200_OK
        )