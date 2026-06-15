# apps/listings/models.py

from django.db import models
from django.conf import settings

class Listing(models.Model):
    PROPERTY_TYPES = [
        ('single_room', 'Single Room'),
        ('two_rooms', '2 Rooms'),
        ('flat', 'Flat'),
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('hostel', 'Hostel'),
        ('office', 'Office Space'),
        ('shutter', 'Shutter'),
    ]
    STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    FURNISHED_STATUS = [
        ('furnished', 'Furnished'),
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi-Furnished'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES)
    furnished_status = models.CharField(
        max_length=20, choices=FURNISHED_STATUS, default='unfurnished'
    )

    # Location
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=200, blank=True)
    ward_number = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Pricing
    monthly_rent = models.PositiveIntegerField()
    security_deposit = models.PositiveIntegerField(default=0)
    bills_water = models.BooleanField(default=False)
    bills_electricity = models.BooleanField(default=False)
    bills_internet = models.BooleanField(default=False)

    # Details
    available_date = models.DateField(null=True, blank=True)
    house_rules = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_rented = models.BooleanField(default=False)
    rented_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()


class Facilities(models.Model):
    listing = models.OneToOneField(
        Listing, on_delete=models.CASCADE, related_name='facilities'
    )
    car_parking = models.BooleanField(default=False)
    bike_parking = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    drinking_water = models.BooleanField(default=False)
    water_24_7 = models.BooleanField(default=False)
    attached_bathroom = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    cctv = models.BooleanField(default=False)
    security_guard = models.BooleanField(default=False)
    pet_allowed = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)

    def __str__(self):
        return f"Facilities for {self.listing.title}"


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='listings/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"


class SavedListing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_listings'
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']

    def __str__(self):
        return f"{self.user.email} saved {self.listing.title}"


class ListingReport(models.Model):
    REASONS = [
        ('fake', 'Fake Listing'),
        ('wrong_info', 'Wrong Information'),
        ('already_rented', 'Already Rented'),
        ('fraud', 'Fraud/Scam'),
        ('other', 'Other'),
    ]
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='reports'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    reason = models.CharField(max_length=30, choices=REASONS)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report on {self.listing.title} by {self.reported_by.email}"
    
class Inquiry(models.Model):
    """A conversation thread between a tenant and landlord about a listing."""
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='inquiries'
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_inquiries'
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_inquiries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ['listing', 'tenant']  # one thread per tenant per listing
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant.email} → {self.listing.title}"

    def last_message(self):
        return self.messages.order_by('-sent_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Individual message within an inquiry thread."""
    inquiry = models.ForeignKey(
        Inquiry, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
    
class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # admin can hide if needed

    class Meta:
        unique_together = ['listing', 'reviewer']  # one review per tenant per listing
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.email} → {self.listing.title} ({self.rating}★)"