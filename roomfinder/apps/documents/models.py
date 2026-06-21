# apps/documents/models.py

from django.db import models
from django.conf import settings

class LandlordDocument(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    citizenship_front = models.ImageField(upload_to='documents/citizenship/')
    citizenship_back = models.ImageField(upload_to='documents/citizenship/')
    lalpurja = models.ImageField(upload_to='documents/lalpurja/')
    selfie_image = models.ImageField(upload_to='documents/selfie/')

    # OCR extracted fields
    ocr_extracted_name = models.CharField(max_length=200, blank=True)
    ocr_citizenship_number = models.CharField(max_length=100, blank=True)
    ocr_address = models.CharField(max_length=300, blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Documents for {self.user.email} — {self.verification_status}"

    def is_approved(self):
        return self.verification_status == 'approved'
    
