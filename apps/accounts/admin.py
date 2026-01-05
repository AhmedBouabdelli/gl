from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from apps.accounts.models import (
    User,
    VolunteerProfile,
    OrganizationProfile,
    Address,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email',
        'username',
        'full_name_display',
        'user_type',
        'is_verified',
        'is_active',
        'date_joined',
    ]
    list_filter = ['user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']

    readonly_fields = ['id', 'date_joined', 'last_login']

    fieldsets = (
        (_('Authentication'), {
            'fields': ('id', 'email', 'username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar')
        }),
        (_('User type & verification'), {
            'fields': ('user_type', 'is_verified')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {
            'fields': ('date_joined', 'last_login')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'user_type',
            ),
        }),
    )

    def full_name_display(self, obj):
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'Full name'


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'user_full_name',
        'availability',
        'hours_per_week',
        'wilaya_display',
        'willing_to_travel',
        'created_at',
    ]
    list_filter = ['availability', 'willing_to_travel', 'address__wilaya', 'created_at']
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'bio',
        'address__wilaya',
        'address__city',
    ]

    readonly_fields = ['id', 'created_at', 'updated_at']
    exclude = ['id']  # just hides id from the form; DB uses UUID PK automatically

    # Always show address (required FK) on both add and change
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Profile'), {'fields': ('bio',)}),
        (_('Availability'), {'fields': ('availability', 'hours_per_week')}),
        (_('Location'), {'fields': ('address',)}),
        (_('Travel'), {'fields': ('willing_to_travel', 'max_travel_distance_km')}),
        (_('Metadata'), {'fields': ('created_at', 'updated_at')}),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_full_name(self, obj):
        return obj.user.get_full_name() or '-'
    user_full_name.short_description = 'Full name'

    def wilaya_display(self, obj):
        if obj.address and obj.address.wilaya:
            return obj.address.wilaya
        return '-'
    wilaya_display.short_description = 'Wilaya'


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'user_email',
        'organization_type',
        'wilaya_display',
        'has_website',
        'created_at',
    ]
    list_filter = ['organization_type', 'address__wilaya', 'created_at']
    search_fields = ['name', 'user__email', 'description', 'address__wilaya', 'address__city']

    readonly_fields = ['id', 'created_at', 'updated_at']
    exclude = ['id']

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Organization'), {
            'fields': ('name', 'description', 'organization_type')
        }),
        (_('Contact'), {
            'fields': ('address', 'website_url', 'social_media_url')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def wilaya_display(self, obj):
        if obj.address and obj.address.wilaya:
            return obj.address.wilaya
        return '-'
    wilaya_display.short_description = 'Wilaya'

    def has_website(self, obj):
        if obj.website_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff;">🌐 Visit</a>',
                obj.website_url
            )
        return '-'
    has_website.short_description = 'Website'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['wilaya', 'city', 'has_coordinates', 'created_at']
    list_filter = ['wilaya', 'created_at']
    search_fields = ['city', 'wilaya', 'address_line_1', 'address_line_2']

    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (_('Address'), {
            'fields': ('wilaya', 'city', 'address_line_1', 'address_line_2')
        }),
        (_('Coordinates'), {
            'fields': ('latitude', 'longitude')
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )

    def has_coordinates(self, obj):
        return bool(getattr(obj, 'latitude', None) and getattr(obj, 'longitude', None))
    has_coordinates.short_description = 'GPS'
