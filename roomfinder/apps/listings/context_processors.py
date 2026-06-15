from .models import Listing

def recently_viewed(request):
    """Inject recently viewed listings into every template context."""
    viewed_ids = request.session.get('recently_viewed', [])
    
    if not viewed_ids:
        return {'recently_viewed': []}
    
    # Fetch listings preserving session order
    listings_dict = {
        l.pk: l for l in Listing.objects.filter(
            pk__in=viewed_ids,
            status='approved'
        ).prefetch_related('images')
    }
    
    # Preserve the order from session
    ordered = [listings_dict[pk] for pk in viewed_ids if pk in listings_dict]
    
    return {'recently_viewed': ordered}