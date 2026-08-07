from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'student_id', 'full_name', 'role', 'gender', 'balance', 'is_active')
    list_filter = ('role', 'gender', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'student_id', 'national_id')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Extra Info'), {
            'fields': ('role', 'gender', 'student_id', 'national_id', 'phone', 'balance', 'avatar', 'is_active_student')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Extra Info'), {
            'fields': ('role', 'gender', 'student_id', 'phone', 'balance')
        }),
    )
