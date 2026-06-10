# apps/accounts/notifications.py

from django.core.mail import send_mail
from django.conf import settings


def send_listing_approved_email(listing):
    subject = f'Your listing "{listing.title}" has been approved!'
    message = f"""
Hi {listing.owner.first_name},

Great news! Your listing has been approved and is now live on RoomFinder.

Listing: {listing.title}
Location: {listing.district}, {listing.province}
Monthly Rent: NPR {listing.monthly_rent}

Tenants can now find and contact you about this listing.

View your listing: http://127.0.0.1:8000/listing/{listing.pk}/

Best regards,
RoomFinder Nepal Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [listing.owner.email],
        )
    except Exception:
        print(f'[EMAIL] Approved: {listing.owner.email} — {listing.title}')


def send_listing_rejected_email(listing):
    subject = f'Your listing "{listing.title}" needs attention'
    message = f"""
Hi {listing.owner.first_name},

Unfortunately, your listing could not be approved at this time.

Listing: {listing.title}
Reason: {listing.rejection_reason}

Please review the rejection reason above, make the necessary corrections,
and resubmit your listing for review.

If you have any questions, please contact our support team.

Best regards,
RoomFinder Nepal Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [listing.owner.email],
        )
    except Exception:
        print(f'[EMAIL] Rejected: {listing.owner.email} — {listing.title}')


def send_document_approved_email(doc):
    subject = 'Your documents have been verified — RoomFinder'
    message = f"""
Hi {doc.user.first_name},

Your identity and property documents have been successfully verified!

You can now create room listings on RoomFinder.
Your listings will display the "Verified Owner" and "Verified Property" badges,
which helps tenants trust your listings.

Get started: http://127.0.0.1:8000/listings/create/

Best regards,
RoomFinder Nepal Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [doc.user.email],
        )
    except Exception:
        print(f'[EMAIL] Docs approved: {doc.user.email}')


def send_document_rejected_email(doc):
    subject = 'Action required: Your documents were not verified'
    message = f"""
Hi {doc.user.first_name},

We were unable to verify your submitted documents.

Reason: {doc.rejection_reason}

Please re-upload your documents with the issues corrected.
Upload here: http://127.0.0.1:8000/documents/upload/

Common reasons for rejection:
- Blurry or unreadable images
- Documents appear edited or tampered
- Name mismatch between document and profile
- Selfie does not match citizenship photo

Best regards,
RoomFinder Nepal Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [doc.user.email],
        )
    except Exception:
        print(f'[EMAIL] Docs rejected: {doc.user.email}')