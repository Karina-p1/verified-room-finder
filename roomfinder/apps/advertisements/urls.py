# apps/advertisements/urls.py

from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    path('reveal/<int:listing_id>/', views.reveal_phone, name='reveal_phone'),
    path('confirm/<int:listing_id>/', views.confirm_ad_watched, name='confirm_ad_watched'),
]