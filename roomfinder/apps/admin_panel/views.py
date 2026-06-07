# apps/admin_panel/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from apps.listings.models import Listing, ListingReport
from apps.documents.models import LandlordDocument
from apps.accounts.models import CustomUser


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
        messages.success(request, f'Listing "{listing.title}" approved.')
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
        messages.success(request, f'Listing "{listing.title}" rejected.')
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
        messages.success(request, f'Documents for {doc.user.email} approved.')
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
        messages.success(request, f'Documents for {doc.user.email} rejected.')
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