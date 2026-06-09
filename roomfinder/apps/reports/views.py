# apps/reports/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.listings.models import ListingReport


@login_required
def my_reports(request):
    reports = ListingReport.objects.filter(
        reported_by=request.user
    ).select_related('listing').order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': reports})