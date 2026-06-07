# apps/listings/admin.py

from django.contrib import admin
from .models import Listing, Facilities, ListingImage, SavedListing, ListingReport

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