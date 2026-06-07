# apps/documents/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LandlordDocument
from .forms import DocumentUploadForm

@login_required
def upload_documents(request):
    # Only landlords can upload documents
    if request.user.role != 'landlord':
        messages.error(request, 'Only landlords can upload verification documents.')
        return redirect('listings:homepage')

    # Check if documents already exist
    existing = LandlordDocument.objects.filter(user=request.user).first()

    # If already approved, no need to re-upload
    if existing and existing.verification_status == 'approved':
        messages.info(request, 'Your documents are already verified.')
        return redirect('listings:my_listings')

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.verification_status = 'pending'
            doc.rejection_reason = ''
            doc.ocr_extracted_name = ''
            doc.ocr_citizenship_number = ''
            doc.ocr_address = ''
            doc.save()
            messages.success(
                request,
                'Documents submitted successfully! '
                'An admin will review them shortly. '
                'You will be notified once verified.'
            )
            return redirect('documents:status')
    else:
        form = DocumentUploadForm(instance=existing)

    return render(request, 'documents/upload.html', {
        'form': form,
        'existing': existing,
    })


@login_required
def document_status(request):
    if request.user.role != 'landlord':
        return redirect('listings:homepage')

    doc = LandlordDocument.objects.filter(user=request.user).first()
    return render(request, 'documents/status.html', {'doc': doc})