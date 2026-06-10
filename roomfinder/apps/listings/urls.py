# apps/listings/urls.py

from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('listing/<int:pk>/', views.listing_detail, name='detail'),
    path('create/', views.create_listing, name='create_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('edit/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('save/<int:pk>/', views.save_listing, name='save_listing'),
    path('saved/', views.saved_listings, name='saved_listings'),
    path('report/<int:pk>/', views.report_listing, name='report_listing'),
    path('ajax/districts/', views.get_districts, name='get_districts'),
    path('mark-rented/<int:pk>/', views.mark_rented, name='mark_rented'),
]