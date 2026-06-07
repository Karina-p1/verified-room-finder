# apps/documents/urls.py

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/', views.upload_documents, name='upload'),
    path('status/', views.document_status, name='status'),
]