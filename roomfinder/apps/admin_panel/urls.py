# apps/admin_panel/urls.py

from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('listings/pending/', views.pending_listings, name='pending_listings'),
    path('listings/approved/', views.approved_listings, name='approved_listings'),
    path('listings/rejected/', views.rejected_listings, name='rejected_listings'),
    path('listings/<int:pk>/review/', views.review_listing, name='review_listing'),
    path('listings/<int:pk>/approve/', views.approve_listing, name='approve_listing'),
    path('listings/<int:pk>/reject/', views.reject_listing, name='reject_listing'),
    path('listings/<int:pk>/remove/', views.remove_listing, name='remove_listing'),

    path('documents/pending/', views.pending_documents, name='pending_documents'),
    path('documents/approved/', views.approved_documents, name='approved_documents'),
    path('documents/rejected/', views.rejected_documents, name='rejected_documents'),
    path('documents/<int:pk>/review/', views.review_document, name='review_document'),
    path('documents/<int:pk>/approve/', views.approve_document, name='approve_document'),
    path('documents/<int:pk>/reject/', views.reject_document, name='reject_document'),

    path('users/', views.user_management, name='user_management'),
    path('users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user_active'),

    path('reports/', views.reports_queue, name='reports_queue'),
    path('reports/<int:pk>/resolve/', views.resolve_report, name='resolve_report'),
    path('ads/', views.manage_ads, name='manage_ads'),
    path('ads/<int:pk>/toggle/', views.toggle_ad, name='toggle_ad'),

    path('analytics/', views.revenue_analytics, name='analytics'),

    path(
    'documents/<int:pk>/result/',
    views.document_verification_result,
    name='document_verification_result'
),
    
]