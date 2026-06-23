# apps/advertisements/models.py

from django.db import models
from django.utils import timezone
from django.db.models import Q


class ActiveAdManager(models.Manager):
    """Returns only ads that are active AND within their scheduled date window."""

    def currently_running(self, position=None):
        now = timezone.now()
        qs = self.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )
        if position:
            qs = qs.filter(position=position)
        return qs


class Advertisement(models.Model):
    POSITIONS = [
        ('homepage_top', 'Homepage Top Banner'),
        ('homepage_between', 'Homepage Between Cards'),
        ('listing_detail', 'Listing Detail Below Images'),
        ('phone_reveal', 'Phone Reveal Rewarded Ad'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    video = models.FileField(upload_to='ads/videos/', blank=True, null=True)
    link_url = models.URLField(blank=True)
    position = models.CharField(max_length=30, choices=POSITIONS)
    is_active = models.BooleanField(default=True)
    duration_seconds = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    # Scheduling fields
    start_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Ad won't show before this date. Leave blank to start immediately."
    )
    end_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Ad won't show after this date. Leave blank to run indefinitely."
    )

    objects = models.Manager()       # default manager — used by admin, dashboard counts, etc.
    active = ActiveAdManager()        # scheduling-aware manager — used for display logic

    def __str__(self):
        return f"{self.title} — {self.get_position_display()}"

    @property
    def is_video(self):
        return bool(self.video)

    def is_currently_active(self):
        """True if is_active AND within the scheduled date window."""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def schedule_status(self):
        """Human-readable status for admin display."""
        if not self.is_active:
            return 'inactive'
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return 'scheduled'
        if self.end_date and now > self.end_date:
            return 'expired'
        return 'running'


class PhoneRevealLog(models.Model):
    """Tracks how many times phone numbers were revealed — for analytics."""
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.CASCADE, related_name='reveal_logs'
    )
    revealed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Reveal for {self.listing.title} at {self.revealed_at}"