from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Address


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('User Profile')
    fk_name = 'user'


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('full_name', 'phone', 'address_line', 'city', 'country', 'is_default')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    inlines = (UserProfileInline, AddressInline)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password', 'phone', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'address_line', 'city', 'country', 'is_default')
    list_filter = ('is_default', 'country', 'city')
    search_fields = ('user__email', 'full_name', 'phone', 'address_line', 'city')
