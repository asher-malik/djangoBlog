from django.contrib import admin
from .models import User, Token
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'username', 'is_admin', 'is_staff', 'is_active')

    # Fields to filter by in the admin list view
    list_filter = ('is_admin', 'is_staff', 'is_active')

    # Fields to search by in the admin list view
    search_fields = ('email', 'username')

    # Fieldsets for the add/edit user page
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active','is_verified', 'is_superuser', 'groups', 'user_permissions')}),
        ('Profile', {'fields': ('profile_picture',)}),
    )

    # Fieldsets for the add user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_admin', 'is_staff', 'is_active', 'is_verified'),
        }),
    )

    # Order users by email in the admin list view
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Token)