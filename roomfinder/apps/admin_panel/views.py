# apps/admin_panel/views.py
import datetime
from django.db.models import Count
from django.db.models.functions import TruncDate
from apps.advertisements.models import PhoneRevealLog, Advertisement

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from apps.listings.models import Listing, ListingReport
from apps.documents.models import LandlordDocument
from apps.accounts.models import CustomUser
from apps.advertisements.models import Advertisement
from apps.accounts.notifications import (
    send_listing_approved_email,
    send_listing_rejected_email,
    send_document_approved_email,
    send_document_rejected_email,
)

@staff_member_required
def revenue_analytics(request):
    from django.utils import timezone
    import datetime

    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

    # Daily phone reveals for chart (last 30 days)
    daily_reveals = (
        PhoneRevealLog.objects
        .filter(revealed_at__gte=thirty_days_ago)
        .annotate(day=TruncDate('revealed_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Top listings by reveal count
    top_listings = (
        PhoneRevealLog.objects
        .values('listing__title', 'listing__pk', 'listing__district')
        .annotate(reveal_count=Count('id'))
        .order_by('-reveal_count')[:10]
    )

    # User growth (joined last 30 days)
    new_users = (
        CustomUser.objects
        .filter(date_joined__gte=thirty_days_ago)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Listing stats by province
    listings_by_province = (
        Listing.objects
        .filter(status='approved')
        .values('province')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    context = {
        # Summary cards
        'total_reveals': PhoneRevealLog.objects.count(),
        'reveals_this_month': PhoneRevealLog.objects.filter(
            revealed_at__gte=thirty_days_ago
        ).count(),
        'total_users': CustomUser.objects.count(),
        'new_users_month': CustomUser.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count(),
        'landlord_count': CustomUser.objects.filter(role='landlord').count(),
        'tenant_count': CustomUser.objects.filter(role='tenant').count(),
        'total_listings': Listing.objects.count(),
        'approved_listings': Listing.objects.filter(status='approved').count(),
        'pending_listings': Listing.objects.filter(status='pending').count(),
        'rejected_listings': Listing.objects.filter(status='rejected').count(),
        'active_ads': Advertisement.objects.filter(is_active=True).count(),

        # Chart data (convert to JSON-safe format)
        'daily_reveals_labels': [str(r['day']) for r in daily_reveals],
        'daily_reveals_data': [r['count'] for r in daily_reveals],
        'new_users_labels': [str(r['day']) for r in new_users],
        'new_users_data': [r['count'] for r in new_users],
        'province_labels': [r['province'] for r in listings_by_province],
        'province_data': [r['count'] for r in listings_by_province],

        # Tables
        'top_listings': top_listings,
    }
    return render(request, 'admin_panel/analytics.html', context)

@staff_member_required
def dashboard(request):
    context = {
        'total_users': CustomUser.objects.count(),
        'total_listings': Listing.objects.count(),
        'pending_listings': Listing.objects.filter(status='pending').count(),
        'approved_listings': Listing.objects.filter(status='approved').count(),
        'rejected_listings': Listing.objects.filter(status='rejected').count(),
        'pending_documents': LandlordDocument.objects.filter(verification_status='pending').count(),
        'total_reports': ListingReport.objects.filter(is_resolved=False).count(),
        'recent_listings': Listing.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required
def pending_listings(request):
    listings = Listing.objects.filter(status='pending').select_related(
        'owner', 'owner__documents'
    ).prefetch_related('images').order_by('-created_at')
    return render(request, 'admin_panel/pending_listings.html', {'listings': listings})


@staff_member_required
def approved_listings(request):
    listings = Listing.objects.filter(status='approved').select_related(
        'owner'
    ).prefetch_related('images').order_by('-created_at')
    return render(request, 'admin_panel/approved_listings.html', {'listings': listings})


@staff_member_required
def rejected_listings(request):
    listings = Listing.objects.filter(status='rejected').select_related(
        'owner'
    ).prefetch_related('images').order_by('-created_at')
    return render(request, 'admin_panel/rejected_listings.html', {'listings': listings})


@staff_member_required
def review_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    doc = LandlordDocument.objects.filter(user=listing.owner).first()
    return render(request, 'admin_panel/review_listing.html', {
        'listing': listing,
        'doc': doc,
    })


@staff_member_required
def approve_listing(request, pk):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=pk)
        listing.status = 'approved'
        listing.rejection_reason = ''
        listing.save()
        doc = LandlordDocument.objects.filter(user=listing.owner).first()
        if doc and doc.verification_status != 'approved':
            doc.verification_status = 'approved'
            doc.reviewed_at = timezone.now()
            doc.save()
        send_listing_approved_email(listing)
        messages.success(request, f'Listing "{listing.title}" approved. Landlord notified.')
    return redirect('admin_panel:pending_listings')


@staff_member_required
def reject_listing(request, pk):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=pk)
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a rejection reason.')
            return redirect('admin_panel:review_listing', pk=pk)
        listing.status = 'rejected'
        listing.rejection_reason = reason
        listing.save()
        send_listing_rejected_email(listing)
        messages.success(request, f'Listing "{listing.title}" rejected. Landlord notified.')
    return redirect('admin_panel:pending_listings')


@staff_member_required
def remove_listing(request, pk):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=pk)
        title = listing.title
        listing.delete()
        messages.success(request, f'Listing "{title}" removed.')
    return redirect('admin_panel:approved_listings')


@staff_member_required
def pending_documents(request):
    docs = LandlordDocument.objects.filter(
        verification_status='pending'
    ).select_related('user').order_by('-submitted_at')
    return render(request, 'admin_panel/pending_documents.html', {'docs': docs})


@staff_member_required
def review_document(request, pk):
    doc = get_object_or_404(LandlordDocument, pk=pk)
    return render(request, 'admin_panel/review_document.html', {'doc': doc})


@staff_member_required
def approve_document(request, pk):
    if request.method == 'POST':
        doc = get_object_or_404(LandlordDocument, pk=pk)
        doc.verification_status = 'approved'
        doc.reviewed_at = timezone.now()
        doc.rejection_reason = ''
        doc.save()
        send_document_approved_email(doc)
        messages.success(request, f'Documents for {doc.user.email} approved. Landlord notified.')
    return redirect('admin_panel:pending_documents')


@staff_member_required
def reject_document(request, pk):
    if request.method == 'POST':
        doc = get_object_or_404(LandlordDocument, pk=pk)
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a rejection reason.')
            return redirect('admin_panel:review_document', pk=pk)
        doc.verification_status = 'rejected'
        doc.rejection_reason = reason
        doc.reviewed_at = timezone.now()
        doc.save()
        send_document_rejected_email(doc)
        messages.success(request, f'Documents for {doc.user.email} rejected. Landlord notified.')
    return redirect('admin_panel:pending_documents')


@staff_member_required
def user_management(request):
    users = CustomUser.objects.annotate(
        listing_count=Count('listings')
    ).order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@staff_member_required
def toggle_user_active(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user:
            messages.error(request, "You can't suspend yourself.")
            return redirect('admin_panel:user_management')
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'suspended'
        messages.success(request, f'User {user.email} {status}.')
    return redirect('admin_panel:user_management')


@staff_member_required
def reports_queue(request):
    reports = ListingReport.objects.filter(
        is_resolved=False
    ).select_related('listing', 'reported_by').order_by('-created_at')
    return render(request, 'admin_panel/reports.html', {'reports': reports})


@staff_member_required
def resolve_report(request, pk):
    if request.method == 'POST':
        report = get_object_or_404(ListingReport, pk=pk)
        report.is_resolved = True
        report.save()
        messages.success(request, 'Report resolved.')
    return redirect('admin_panel:reports_queue')


@staff_member_required
def manage_ads(request):
    ads = Advertisement.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/ads.html', {'ads': ads})


@staff_member_required
def toggle_ad(request, pk):
    if request.method == 'POST':
        ad = get_object_or_404(Advertisement, pk=pk)
        ad.is_active = not ad.is_active
        ad.save()
        messages.success(request, f'Ad "{ad.title}" {"activated" if ad.is_active else "deactivated"}.')
    return redirect('admin_panel:manage_ads')