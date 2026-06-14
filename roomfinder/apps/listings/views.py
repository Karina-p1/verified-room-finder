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


@login_required
def my_reports(request):
    reports = ListingReport.objects.filter(
        reported_by=request.user
    ).select_related('listing').order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': reports})

def homepage(request):
    listings = Listing.objects.filter(status='approved', is_rented=False).prefetch_related('images', 'facilities')

    # Search
    q = request.GET.get('q', '')
    province = request.GET.get('province', '')
    district = request.GET.get('district', '')
    property_type = request.GET.get('property_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    wifi = request.GET.get('wifi', '')
    attached_bathroom = request.GET.get('attached_bathroom', '')
    pet_allowed = request.GET.get('pet_allowed', '')
    sort = request.GET.get('sort', 'latest')

    if q:
        listings = listings.filter(
            Q(title__icontains=q) | Q(description__icontains=q) |
            Q(city__icontains=q) | Q(district__icontains=q)
        )
    if province:
        listings = listings.filter(province=province)
    if district:
        listings = listings.filter(district=district)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if min_price:
        listings = listings.filter(monthly_rent__gte=min_price)
    if max_price:
        listings = listings.filter(monthly_rent__lte=max_price)
    if wifi:
        listings = listings.filter(facilities__wifi=True)
    if attached_bathroom:
        listings = listings.filter(facilities__attached_bathroom=True)
    if pet_allowed:
        listings = listings.filter(facilities__pet_allowed=True)

    if sort == 'price_low':
        listings = listings.order_by('monthly_rent')
    elif sort == 'price_high':
        listings = listings.order_by('-monthly_rent')
    else:
        listings = listings.order_by('-created_at')

    # Paginate — 12 listings per page
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Insert ads every 5 cards (paginated list only)
    listing_list = list(page_obj)
    with_ads = []
    for i, listing in enumerate(listing_list):
        with_ads.append({'type': 'listing', 'obj': listing})
        if (i + 1) % 5 == 0 and i + 1 < len(listing_list):
            with_ads.append({'type': 'ad'})

    # Get banner ads
    from apps.advertisements.models import Advertisement
    top_banner = Advertisement.objects.filter(
        position='homepage_top', is_active=True
    ).order_by('?').first()

    context = {
        'listings': with_ads,
        'page_obj': page_obj,
        'districts': DISTRICTS,
        'top_banner': top_banner,
        'total_count': paginator.count,
        'current_filters': {
            'q': q, 'province': province, 'district': district,
            'property_type': property_type, 'min_price': min_price,
            'max_price': max_price, 'sort': sort,
        }
    }
    return render(request, 'listings/homepage.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status='approved')
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