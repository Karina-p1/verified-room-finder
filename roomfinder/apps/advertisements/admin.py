# apps/advertisements/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement, PhoneRevealLog


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'position', 'is_active', 'schedule_status_display',
        'start_date', 'end_date', 'duration_seconds', 'created_at',
    ]
    list_filter = ['position', 'is_active']
    list_editable = ['is_active']
    fields = [
        'title', 'image', 'link_url', 'position',
        'is_active', 'duration_seconds',
        'start_date', 'end_date',
    ]

    def schedule_status_display(self, obj):
        status = obj.schedule_status()
        colors = {
            'running': 'green',
            'scheduled': 'blue',
            'expired': 'gray',
            'inactive': 'red',
        }
        return format_html(
            '<b style="color:{};">{}</b>',
            colors.get(status, 'black'),
            status.upper()
        )
    schedule_status_display.short_description = 'Status'


@admin.register(PhoneRevealLog)
class PhoneRevealLogAdmin(admin.ModelAdmin):
    list_display = ['listing', 'revealed_at', 'ip_address']
    readonly_fields = ['listing', 'revealed_at', 'ip_address']