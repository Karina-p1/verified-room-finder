# apps/documents/admin.py

from django.contrib import admin
from .models import LandlordDocument

@admin.register(LandlordDocument)
class LandlordDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'verification_status', 'submitted_at', 'reviewed_at']
    list_filter = ['verification_status']
    search_fields = ['user__email', 'ocr_extracted_name']
    readonly_fields = [
        'citizenship_front', 'citizenship_back',
        'lalpurja', 'selfie_image',
        'ocr_extracted_name', 'ocr_citizenship_number',
        'ocr_address', 'submitted_at',
    ]