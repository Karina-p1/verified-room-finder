# apps/listings/admin.py

from django.contrib import admin
from .models import Listing, Facilities, ListingImage, SavedListing, ListingReport
from .models import Inquiry, Message
from .models import Review
class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 0

class FacilitiesInline(admin.StackedInline):
    model = Facilities

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'property_type', 'district', 'monthly_rent', 'status', 'created_at']
    list_filter = ['status', 'property_type', 'province']
    search_fields = ['title', 'owner__email', 'district']
    inlines = [FacilitiesInline, ListingImageInline]

admin.site.register(SavedListing)
admin.site.register(ListingReport)

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'body', 'sent_at', 'is_read']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['listing', 'tenant', 'landlord', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tenant__email', 'landlord__email', 'listing__title']
    inlines = [MessageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'listing', 'reviewer', 'rating', 'title', 'is_approved', 'created_at'
    ]
    list_filter = ['rating', 'is_approved']
    list_editable = ['is_approved']
    search_fields = ['reviewer__email', 'listing__title', 'title']
    readonly_fields = ['listing', 'reviewer', 'landlord', 'created_at']

