# apps/advertisements/admin.py

from django.contrib import admin
from .models import Advertisement, PhoneRevealLog

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'duration_seconds', 'created_at']
    list_filter = ['position', 'is_active']
    list_editable = ['is_active']

@admin.register(PhoneRevealLog)
class PhoneRevealLogAdmin(admin.ModelAdmin):
    list_display = ['listing', 'revealed_at', 'ip_address']
    readonly_fields = ['listing', 'revealed_at', 'ip_address']