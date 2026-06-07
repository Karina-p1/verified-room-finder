# apps/advertisements/models.py

from django.db import models

class Advertisement(models.Model):
    POSITIONS = [
        ('homepage_top', 'Homepage Top Banner'),
        ('homepage_between', 'Homepage Between Cards'),
        ('listing_detail', 'Listing Detail Below Images'),
        ('phone_reveal', 'Phone Reveal Rewarded Ad'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/')
    link_url = models.URLField(blank=True)
    position = models.CharField(max_length=30, choices=POSITIONS)
    is_active = models.BooleanField(default=True)
    duration_seconds = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.get_position_display()}"


class PhoneRevealLog(models.Model):
    """Tracks how many times phone numbers were revealed — for analytics."""
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.CASCADE, related_name='reveal_logs'
    )
    revealed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Reveal for {self.listing.title} at {self.revealed_at}"