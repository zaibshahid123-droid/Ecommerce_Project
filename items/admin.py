from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date_of_birth', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username', 'user__email')
    fields = ('user', 'date_of_birth', 'role', 'is_approved')