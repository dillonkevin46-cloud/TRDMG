from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'role')
    list_filter = ('role', 'department', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Tradecore Roles & Department', {'fields': ('role', 'department', 'manager')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tradecore Roles & Department', {
            'classes': ('wide',),
            'fields': ('role', 'department', 'manager'),
        }),
    )
    ordering = ('username',)
