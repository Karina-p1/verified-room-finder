# apps/advertisements/views.py

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Advertisement, PhoneRevealLog
from apps.listings.models import Listing


def get_ad(position):
    """Helper — returns a random currently-running ad (active + within schedule) for a given position."""
    return Advertisement.active.currently_running(position=position).order_by('?').first()


@login_required
def reveal_phone(request, listing_id):
    """Step 1 — tenant clicks Reveal. Return ad to watch."""
    session_key = f'revealed_{listing_id}'

    # Already revealed this session — return phone directly
    if request.session.get(session_key):
        listing = get_object_or_404(Listing, pk=listing_id, status='approved')
        return JsonResponse({'already_revealed': True, 'phone': listing.owner.phone})

    # Get a rewarded ad to show
    ad = get_ad('phone_reveal')
    if ad:
        return JsonResponse({
            'show_ad': True,
            'ad_id': ad.id,
            'ad_image': ad.image.url,
            'ad_link': ad.link_url,
            'ad_duration': ad.duration_seconds,
        })
    else:
        # No ad currently running — reveal directly
        listing = get_object_or_404(Listing, pk=listing_id, status='approved')
        request.session[session_key] = True
        return JsonResponse({'already_revealed': True, 'phone': listing.owner.phone})


@login_required
@require_POST
def confirm_ad_watched(request, listing_id):
    """Step 2 — called after ad countdown finishes. Returns phone number."""
    listing = get_object_or_404(Listing, pk=listing_id, status='approved')

    # Cache in session so ad isn't shown again
    request.session[f'revealed_{listing_id}'] = True

    # Log the reveal for analytics
    PhoneRevealLog.objects.create(
        listing=listing,
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    return JsonResponse({'phone': listing.owner.phone})