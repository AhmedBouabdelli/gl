from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.serializers import (
    UserDetailSerializer,
    UserUpdateSerializer,
)
from apps.accounts.permissions import IsOwnerOrAdmin
from apps.accounts.services import UserService


class CurrentUserView(generics.RetrieveAPIView):
    """Get current authenticated user details"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(
            {
                'user': serializer.data,
                'message': 'User details retrieved successfully.'
            },
            status=status.HTTP_200_OK
        )


class UserDetailView(generics.RetrieveAPIView):
    """Get specific user details by ID"""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(
            {
                'user': serializer.data,
                'message': 'User details retrieved successfully.'
            },
            status=status.HTTP_200_OK
        )


class UserUpdateView(generics.UpdateAPIView):
    """Update current user profile"""
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

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

        user_serializer = UserDetailSerializer(
            instance,
            context={'request': request}
        )

        return Response(
            {
                'user': user_serializer.data,
                'message': 'Profile updated successfully.'
            },
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """List all active users with optional filtering"""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user type if provided
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        # Filter by search term if provided
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return queryset.order_by('-date_joined')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'count': queryset.count(),
                'results': serializer.data,
                'message': 'Users retrieved successfully.'
            },
            status=status.HTTP_200_OK
        )


class DeactivateAccountView(generics.GenericAPIView):
    """Deactivate current user account"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        reason = request.data.get('reason', '')

        try:
            UserService.deactivate_account(user, reason=reason)

            return Response(
                {'message': 'Account deactivated successfully.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReactivateAccountView(generics.GenericAPIView):
    """Reactivate current user account"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            UserService.reactivate_account(user)

            return Response(
                {'message': 'Account reactivated successfully.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )