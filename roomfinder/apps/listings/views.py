# apps/listings/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from urllib3 import request
from .models import Listing, ListingImage, SavedListing, ListingReport
from .forms import ListingForm, FacilitiesForm, ListingReportForm
from apps.advertisements.models import Advertisement
from apps.listings.models import ListingReport
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Inquiry, Message
from .forms import InquiryMessageForm
from .models import Review
from .forms import ReviewForm
from django.db.models import Avg

DISTRICTS = {
    'Koshi': ['Taplejung', 'Sankhuwasabha', 'Solukhumbu', 'Okhaldhunga',
              'Khotang', 'Bhojpur', 'Dhankuta', 'Terhathum', 'Panchthar',
              'Ilam', 'Jhapa', 'Morang', 'Sunsari', 'Udayapur'],
    'Madhesh': ['Saptari', 'Siraha', 'Dhanusha', 'Mahottari',
                'Sarlahi', 'Rautahat', 'Bara', 'Parsa'],
    'Bagmati': ['Kathmandu', 'Lalitpur', 'Bhaktapur', 'Kavrepalanchok',
                'Sindhupalchok', 'Rasuwa', 'Nuwakot', 'Dhading',
                'Makwanpur', 'Chitwan', 'Sindhuli', 'Ramechhap', 'Dolakha'],
    'Gandaki': ['Kaski', 'Syangja', 'Parbat', 'Baglung', 'Myagdi',
                'Mustang', 'Manang', 'Lamjung', 'Tanahu', 'Gorkha',
                'Nawalpur', 'Palpa'],
    'Lumbini': ['Rupandehi', 'Kapilvastu', 'Nawalparasi', 'Arghakhanchi',
                'Gulmi', 'Palpa', 'Dang', 'Pyuthan', 'Rolpa',
                'Eastern Rukum', 'Banke', 'Bardiya'],
    'Karnali': ['Surkhet', 'Dailekh', 'Jajarkot', 'Western Rukum',
                'Salyan', 'Dolpa', 'Humla', 'Jumla', 'Kalikot', 'Mugu'],
    'Sudurpashchim': ['Kailali', 'Kanchanpur', 'Dadeldhura', 'Baitadi',
                      'Darchula', 'Bajhang', 'Bajura', 'Achham', 'Doti'],
}
def track_recently_viewed(request, listing_id):
    """Store last 6 viewed listing IDs in session."""
    viewed = request.session.get('recently_viewed', [])
    
    # Remove if already exists (to re-add at front)
    if listing_id in viewed:
        viewed.remove(listing_id)
    
    # Add to front
    viewed.insert(0, listing_id)
    
    # Keep only last 6
    viewed = viewed[:6]
    
    request.session['recently_viewed'] = viewed
    request.session.modified = True

@require_POST
def clear_recently_viewed(request):
    """AJAX — clears recently viewed from session."""
    from django.http import JsonResponse
    request.session['recently_viewed'] = []
    request.session.modified = True
    return JsonResponse({'status': 'cleared'})

@login_required
def start_inquiry(request, listing_pk):
    """Tenant starts or continues an inquiry thread."""
    listing = get_object_or_404(Listing, pk=listing_pk, status='approved')

    # Only tenants can start inquiries
    if request.user.role != 'tenant':
        messages.error(request, 'Only tenants can send inquiries.')
        return redirect('listings:detail', pk=listing_pk)

    # Prevent tenant messaging their own listing
    if listing.owner == request.user:
        messages.error(request, 'You cannot message yourself.')
        return redirect('listings:detail', pk=listing_pk)

    # Get or create inquiry thread
    inquiry, created = Inquiry.objects.get_or_create(
        listing=listing,
        tenant=request.user,
        defaults={'landlord': listing.owner}
    )

    if request.method == 'POST':
        form = InquiryMessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                inquiry=inquiry,
                sender=request.user,
                body=form.cleaned_data['body'],
            )
            messages.success(request, 'Message sent!')
            return redirect('listings:inquiry_thread', pk=inquiry.pk)
    else:
        form = InquiryMessageForm()

    return render(request, 'listings/inquiry_start.html', {
        'listing': listing,
        'inquiry': inquiry,
        'form': form,
        'created': created,
    })


@login_required
def inquiry_thread(request, pk):
    """View and reply in a conversation thread."""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    # Only tenant or landlord of this inquiry can view it
    if request.user not in [inquiry.tenant, inquiry.landlord]:
        messages.error(request, 'Access denied.')
        return redirect('listings:homepage')

    # Mark messages as read
    inquiry.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    form = InquiryMessageForm()

    if request.method == 'POST':
        form = InquiryMessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                inquiry=inquiry,
                sender=request.user,
                body=form.cleaned_data['body'],
            )
            return redirect('listings:inquiry_thread', pk=pk)

    return render(request, 'listings/inquiry_thread.html', {
        'inquiry': inquiry,
        'form': form,
        'other_user': inquiry.landlord if request.user == inquiry.tenant
                      else inquiry.tenant,
    })


@login_required
def my_inquiries(request):
    """List all inquiry threads for the logged-in user."""
    if request.user.role == 'tenant':
        inquiries = Inquiry.objects.filter(
            tenant=request.user
        ).select_related(
            'listing', 'landlord'
        ).prefetch_related('messages')
    else:
        # Landlord sees received inquiries
        inquiries = Inquiry.objects.filter(
            landlord=request.user
        ).select_related(
            'listing', 'tenant'
        ).prefetch_related('messages')

    # Attach unread count to each inquiry
    for inquiry in inquiries:
        inquiry.unread = inquiry.unread_count(request.user)

    return render(request, 'listings/my_inquiries.html', {
        'inquiries': inquiries,
    })

@login_required
def my_reports(request):
    reports = ListingReport.objects.filter(
        reported_by=request.user
    ).select_related('listing').order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': reports})

def homepage(request):
    listings_qs = Listing.objects.filter(
        status='approved',
        is_rented=False
    ).prefetch_related('images', 'facilities')

    q                = request.GET.get('q', '')
    province         = request.GET.get('province', '')
    district         = request.GET.get('district', '')
    property_type    = request.GET.get('property_type', '')
    furnished_status = request.GET.get('furnished_status', '')
    min_price        = request.GET.get('min_price', '')
    max_price        = request.GET.get('max_price', '')
    sort             = request.GET.get('sort', 'latest')

    if q:
        listings_qs = listings_qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q) |
            Q(city__icontains=q)  | Q(district__icontains=q)
        )
    if province:         listings_qs = listings_qs.filter(province=province)
    if district:         listings_qs = listings_qs.filter(district=district)
    if property_type:    listings_qs = listings_qs.filter(property_type=property_type)
    if furnished_status: listings_qs = listings_qs.filter(furnished_status=furnished_status)
    if min_price:        listings_qs = listings_qs.filter(monthly_rent__gte=min_price)
    if max_price:        listings_qs = listings_qs.filter(monthly_rent__lte=max_price)

    for facility in ['wifi', 'attached_bathroom', 'car_parking',
                     'pet_allowed', 'kitchen', 'water_24_7', 'balcony', 'cctv']:
        if request.GET.get(facility):
            listings_qs = listings_qs.filter(**{f'facilities__{facility}': True})

    if sort == 'price_low':
        listings_qs = listings_qs.order_by('monthly_rent')
    elif sort == 'price_high':
        listings_qs = listings_qs.order_by('-monthly_rent')
    else:
        listings_qs = listings_qs.order_by('-created_at')

    paginator   = Paginator(listings_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    listing_list = list(page_obj)
    with_ads = []
    for i, listing in enumerate(listing_list):
        with_ads.append({'type': 'listing', 'obj': listing})
        if (i + 1) % 6 == 0 and i + 1 < len(listing_list):
            with_ads.append({'type': 'ad'})

    top_banner = Advertisement.objects.filter(
        position='homepage_top', is_active=True
    ).order_by('?').first()

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('sort', None)
    query_string = query_params.urlencode()

    active_filter_count = sum(
        1 for k, v in request.GET.items()
        if k not in ['page', 'sort'] and v
    )

    context = {
        'listings':            with_ads,
        'page_obj':            page_obj,
        'total_count':         paginator.count,
        'districts':           DISTRICTS,
        'provinces':           list(DISTRICTS.keys()),
        'top_banner':          top_banner,
        'query_string':        query_string,
        'has_active_filters':  active_filter_count > 0,
        'active_filter_count': active_filter_count,
        'current_filters': {
            'q': q, 'province': province, 'district': district,
            'property_type': property_type, 'furnished_status': furnished_status,
            'min_price': min_price, 'max_price': max_price, 'sort': sort,
        }
    }
    return render(request, 'listings/homepage.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status='approved')

    # Track recently viewed
    track_recently_viewed(request, pk)

    # Similar listings — same district first, fallback to same province
    similar = Listing.objects.filter(
        status='approved',
        is_rented=False
    ).exclude(pk=pk)

    # Try same district + property type first (best match)
    similar_listings = similar.filter(
        district=listing.district,
        property_type=listing.property_type,
    ).prefetch_related('images')[:3]

    # Not enough? Fill with same district any type
    if similar_listings.count() < 3:
        exclude_pks = [pk] + list(similar_listings.values_list('pk', flat=True))
        extra = similar.filter(
            district=listing.district
        ).exclude(
            pk__in=exclude_pks
        ).prefetch_related('images')[:3 - similar_listings.count()]
        similar_listings = list(similar_listings) + list(extra)

    # Still not enough? Fill with same province
    if len(similar_listings) < 3:
        exclude_pks = [pk] + [l.pk for l in similar_listings]
        extra = similar.filter(
            province=listing.province
        ).exclude(
            pk__in=exclude_pks
        ).prefetch_related('images')[:3 - len(similar_listings)]
        similar_listings = list(similar_listings) + list(extra)

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedListing.objects.filter(
            user=request.user, listing=listing
        ).exists()

    report_form = ListingReportForm()

    return render(request, 'listings/detail.html', {
        'listing': listing,
        'is_saved': is_saved,
        'report_form': report_form,
        'similar_listings': similar_listings,
    })


@login_required
def create_listing(request):
    if request.user.role != 'landlord':
        messages.error(request, 'Only landlords can create listings.')
        return redirect('listings:homepage')

    # Check if landlord has uploaded and approved documents
    doc = getattr(request.user, 'documents', None)
    if not doc:
        messages.warning(
            request,
            'You must upload your verification documents before creating a listing.'
        )
        return redirect('documents:upload')
    if doc.verification_status == 'pending':
        messages.warning(request, 'Your documents are still under review. Please wait.')
        return redirect('documents:status')
    if doc.verification_status == 'rejected':
        messages.error(request, 'Your documents were rejected. Please re-upload.')
        return redirect('documents:upload')

    if request.method == 'POST':
        listing_form = ListingForm(request.POST)
        facilities_form = FacilitiesForm(request.POST)
        images = request.FILES.getlist('images')

        if listing_form.is_valid() and facilities_form.is_valid():
            if len(images) < 3:
                messages.error(request, 'Please upload at least 3 images.')
            elif len(images) > 15:
                messages.error(request, 'Maximum 15 images allowed.')
            else:
                listing = listing_form.save(commit=False)
                listing.owner = request.user
                listing.status = 'pending'
                listing.save()
                facilities = facilities_form.save(commit=False)
                facilities.listing = listing
                facilities.save()
                for i, img in enumerate(images):
                    ListingImage.objects.create(
                        listing=listing,
                        image=img,
                        is_primary=(i == 0)
                    )
                messages.success(request, 'Listing submitted! Pending admin approval.')
                return redirect('listings:my_listings')
    else:
        listing_form = ListingForm()
        facilities_form = FacilitiesForm()

    return render(request, 'listings/create_listing.html', {
        'listing_form': listing_form,
        'facilities_form': facilities_form,
        'districts': DISTRICTS,
    })

@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).prefetch_related('images')
    return render(request, 'listings/my_listings.html', {'listings': listings})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)

    try:
        facilities_instance = listing.facilities
    except Exception:
        facilities_instance = None

    if request.method == 'POST':
        listing_form = ListingForm(request.POST, instance=listing)
        facilities_form = FacilitiesForm(request.POST, instance=facilities_instance)

        # Grab district manually since it's a custom JS-populated select
        district_value = request.POST.get('district', '').strip()

        if listing_form.is_valid() and facilities_form.is_valid():
            updated = listing_form.save(commit=False)
            updated.district = district_value  # ← manually inject it
            updated.status = 'pending'
            updated.rejection_reason = ''
            updated.save()

            fac = facilities_form.save(commit=False)
            fac.listing = updated
            fac.save()

            # Handle optional new images
            new_images = request.FILES.getlist('new_images')
            if new_images:
                current_count = updated.images.count()
                slots_left = 15 - current_count
                if slots_left > 0:
                    for img in new_images[:slots_left]:
                        ListingImage.objects.create(
                            listing=updated,
                            image=img,
                            is_primary=False
                        )
                    if len(new_images) > slots_left:
                        messages.warning(request, f'Only {slots_left} images added — max 15 total.')

            messages.success(request, 'Listing updated and resubmitted for approval.')
            return redirect('listings:my_listings')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        listing_form = ListingForm(instance=listing)
        facilities_form = FacilitiesForm(instance=facilities_instance)

    return render(request, 'listings/edit_listing.html', {
        'listing_form': listing_form,
        'facilities_form': facilities_form,
        'listing': listing,
        'districts': DISTRICTS,
    })

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted.')
    return redirect('listings:my_listings')

@login_required
def delete_listing_image(request, image_id):
    from .models import ListingImage
    image = get_object_or_404(ListingImage, pk=image_id, listing__owner=request.user)
    listing_pk = image.listing.pk
    
    # Don't allow deleting if only 3 images remain
    if image.listing.images.count() <= 3:
        messages.error(request, 'Minimum 3 images required. Cannot delete.')
        return redirect('listings:edit_listing', pk=listing_pk)
    
    # If deleting primary image, make next one primary
    if image.is_primary:
        next_img = image.listing.images.exclude(pk=image.pk).first()
        if next_img:
            next_img.is_primary = True
            next_img.save()
    
    image.delete()
    messages.success(request, 'Image deleted.')
    return redirect('listings:edit_listing', pk=listing_pk)

@login_required
def save_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    saved, created = SavedListing.objects.get_or_create(
        user=request.user, listing=listing
    )
    if not created:
        saved.delete()
        messages.info(request, 'Listing removed from saved.')
    else:
        messages.success(request, 'Listing saved!')
    return redirect('listings:detail', pk=pk)


@login_required
def saved_listings(request):
    saved = SavedListing.objects.filter(user=request.user).select_related('listing')
    return render(request, 'listings/saved_listings.html', {'saved': saved})


@login_required
def report_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        form = ListingReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.listing = listing
            report.reported_by = request.user
            report.save()
            messages.success(request, 'Report submitted. Thank you.')
    return redirect('listings:detail', pk=pk)

@login_required
def mark_rented(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.is_rented = not listing.is_rented
        listing.rented_at = timezone.now() if listing.is_rented else None
        listing.save()
        status = 'marked as rented' if listing.is_rented else 'marked as available'
        messages.success(request, f'Listing "{listing.title}" {status}.')
    return redirect('listings:my_listings')

def get_districts(request):
    """AJAX endpoint — returns districts for a selected province."""
    from django.http import JsonResponse
    province = request.GET.get('province', '')
    districts = DISTRICTS.get(province, [])
    return JsonResponse({'districts': districts})

@login_required
def submit_review(request, listing_pk):
    """Tenant submits a review for a listing/landlord."""
    listing = get_object_or_404(Listing, pk=listing_pk, status='approved')

    # Only tenants can review
    if request.user.role != 'tenant':
        messages.error(request, 'Only tenants can submit reviews.')
        return redirect('listings:detail', pk=listing_pk)

    # Can't review your own listing
    if listing.owner == request.user:
        messages.error(request, 'You cannot review your own listing.')
        return redirect('listings:detail', pk=listing_pk)

    # Check if already reviewed
    existing = Review.objects.filter(
        listing=listing, reviewer=request.user
    ).first()

    if existing:
        messages.info(request, 'You have already reviewed this listing.')
        return redirect('listings:detail', pk=listing_pk)

    # Must have sent an inquiry first (contacted landlord)
    has_inquired = Inquiry.objects.filter(
        listing=listing, tenant=request.user
    ).exists()

    if not has_inquired:
        messages.warning(
            request,
            'You must contact the landlord before leaving a review.'
        )
        return redirect('listings:detail', pk=listing_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.listing = listing
            review.reviewer = request.user
            review.landlord = listing.owner
            review.save()
            messages.success(request, 'Review submitted! Thank you.')
            return redirect('listings:detail', pk=listing_pk)
    else:
        form = ReviewForm()

    return render(request, 'listings/submit_review.html', {
        'listing': listing,
        'form': form,
    })


@login_required
def delete_review(request, pk):
    """Reviewer can delete their own review."""
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    listing_pk = review.listing.pk
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('listings:detail', pk=listing_pk)